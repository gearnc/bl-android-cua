#!/usr/bin/env python3
"""hd — hybrid Android navigation CLI for LLM agents (framework-ADAPTIVE edition, v5).

The observation PRIMITIVE adapts to the detected framework:
  views   -> trees are rich/labeled: prefer `hd see --find PAT` (grep-grade cost);
             plain `hd see` prints a tip when the screen is large.
  compose -> unlabeled clickable nodes are greppable only via near:"label" hints, so the
             rendered compact tree is the default primitive; --find matches hints too.
  rn      -> element state (checked=) is surfaced and --find matches it (e.g.
             `hd see --find 'checked=false'`); re-tap by coords if a tap no-ops.

Perception: `adb shell uiautomator dump` rendered as a compact indexed node list, with
perception defaults auto-tuned to the foreground app's UI framework (Views / Jetpack Compose /
React Native). The app's toolkit capability is probed from its APK once and cached; which
toolkit a given SCREEN renders with is then decided from the tree, since apps mix the two.
Override with HD_PROFILE=views|compose|rn.
Action: coordinate taps/swipes/keys via `adb shell input` (never a11y performAction).
Text: `adb shell input text` (injects below the IME — host-keyboard-proof).
Screenshots: explicit `shot` verb only.

Verbs:
  hd see [--full] [--find PAT]   observe screen; --find prints ONLY nodes matching regex PAT
                                  (case-insensitive, over label/id/class) plus their index —
                                  the cheapest observation when you know what you're looking for
  hd see                          re-observing a screen you have already seen prints only what
                                  CHANGED since your last `see` of the same kind, with current
                                  indexes, so `hd tap` works straight off it. A row that only
                                  scrolled is one `~ [was]->[now] (x,y)` line, not a removal plus
                                  an addition. The whole tree is
                                  printed automatically whenever it is cheaper than the delta or
                                  the last `see` is too old to trust — you never have to ask.
  hd see -q                       observe WITHOUT printing the tree: one header line, the tree
                                  cached on disk. Pair with `hd find`.
  hd find PAT                     grep the cached tree — no adb round-trip, only the matching
                                  lines enter the context. Re-observes if the cache is stale,
                                  and on a miss prints the cached tree rather than asking you
                                  to fetch it, so a miss still costs one look.
                                  `hd see -q; hd find Save` is the cheapest observe-and-locate.
  EVERY action verb OBSERVES AFTER ACTING, by default: it waits for the screen to settle and
                         then prints exactly what the following `hd see` would have — one command
                         instead of two, same output. `hd tap 5 -s Save` narrows that look to what
                         `hd see --find Save` would print. `hd tap 5 -n` suppresses it, which is
                         what you want on every action of a batch except the last:
                         `hd tap 5 -n; hd tap 9 -n; hd tap 3` is one turn and one tree.
                         The look is what costs turns, not tokens.
  hd tap <index>         tap center of node <index> from the LAST `see` (re-verifies first)
  hd tap-xy <x> <y>      raw coordinate tap
  hd longpress <index>   long-press node <index> — THE way to open an item's context menu
                         (rename/delete/copy on list items and files). Try this FIRST when a
                         per-item action has no visible button.
  hd longpress-xy <x> <y>  raw coordinate long-press
  hd type "text"         type into the focused field (appends at the cursor)
  hd type "text" -r      REPLACE the focused field's contents: hd reads its current length off
                         the tree and deletes exactly that many characters before typing, so
                         editing an existing value is one command instead of a guessed
                         `for i in $(seq 30); do adb shell input keyevent 67; done`
  hd clear               same deletion without typing anything
  hd key <name>          back|home|enter|tab|delete or raw keycode number
  hd swipe up|down|left|right [--steps N]
  hd shot <file.png>     screenshot to file
  hd wait-idle [--timeout S]
State file: /tmp/hd_last_tree.json (indexes are only valid against the last `see`).
"""
import collections, json, os, re, shlex, subprocess, sys, time
import xml.etree.ElementTree as ET

ADB = os.environ.get("HD_ADB", "adb")
STATE = "/tmp/hd_last_tree.json"
FW_CACHE = "/tmp/hd_fw_cache.json"
HINTED = "/tmp/hd_hinted_no_see"
COMPACT_MIN_NODES = 5  # F7: auto-escalate below this
DIFF_MAX_AGE = 120     # seconds; past this the previous tree is not a trustworthy baseline

def foreground_pkg():
    out = sh("shell", "dumpsys", "window")
    m = re.search(r"mCurrentFocus=.*?\s([\w.]+)/", out)
    return m.group(1) if m else None

def apk_contains(pkg, needle):
    path_out = sh("shell", "pm", "path", pkg)
    apks = [l.split(":", 1)[1].strip() for l in path_out.splitlines() if l.startswith("package:")]
    for apk in apks:
        if subprocess.run([ADB, "shell", f"grep -qm1 {needle} {apk} 2>/dev/null"]).returncode == 0:
            return True
    return False

def renders_unlabeled(nodes):
    """True when this screen looks Compose-rendered rather than View-rendered.

    Compose emits anonymous `View` nodes carrying neither a resource-id nor text, so they are
    reachable only through adopt_labels' near:"label" hints; inflated Views keep their ids.
    Measured across 25 apps, resource-id density over informative nodes separates them cleanly:
    0.48-0.82 View-rendered vs 0.02-0.15 Compose-rendered, so the threshold sits in the middle
    of that empty band. The share of clickables that are anonymous corroborates it, but only
    once there are enough clickables to be meaningful.
    """
    ID_DENSITY_MAX = 0.35
    informative = [n for n in nodes if is_informative(n)] or nodes
    if not informative:
        return False
    id_frac = sum(1 for n in informative if n["id"]) / len(informative)
    clickable = [n for n in nodes if n["clickable"]]
    anonymous = sum(1 for n in clickable
                    if n["class"] == "View" and not n["text"] and not n["desc"])
    corroborated = len(clickable) < 3 or anonymous / len(clickable) >= 0.5
    return id_frac < ID_DENSITY_MAX and corroborated

def detect_profile(nodes):
    forced = os.environ.get("HD_PROFILE")
    if forced:
        return forced, "(forced)"
    if any(n["class"] == "ComposeView" for n in nodes):
        return "compose", "(ComposeView in tree)"
    pkg = foreground_pkg()
    if not pkg:
        return "views", "(unknown pkg)"
    # The cache holds the package's toolkit CAPABILITY (from its APK, one adb probe per app),
    # never the per-screen verdict: apps mix toolkits screen by screen.
    cache = json.load(open(FW_CACHE)) if os.path.exists(FW_CACHE) else {}
    if pkg not in cache:
        cache[pkg] = ("rn" if apk_contains(pkg, "libreactnative")
                      else "compose-capable" if apk_contains(pkg, "androidx.compose")
                      else "views")
        json.dump(cache, open(FW_CACHE, "w"))
    if cache[pkg] == "rn":
        return "rn", pkg
    if cache[pkg] == "compose-capable":
        # Plenty of Compose apps expose no ComposeView node (Seal, Unitto, InnerTune), so the
        # APK is the only hint they are Compose at all. But shipping Compose does not mean a
        # given screen renders that way --- Material Files draws a fully labeled View tree --- so
        # the tree decides, at zero extra adb cost.
        if not renders_unlabeled(nodes):
            return "views", f"{pkg} (compose in apk, but this screen renders labeled)"
        return "compose", f"{pkg} (compose in apk + unlabeled tree)"
    return "views", pkg

def sh(*args, binary=False, timeout=30):
    r = subprocess.run([ADB, *args], capture_output=True, timeout=timeout)
    if r.returncode != 0:
        sys.exit(f"adb error: {r.stderr.decode(errors='replace').strip()}")
    return r.stdout if binary else r.stdout.decode(errors="replace")

def dump_xml(retries=3):
    for i in range(retries):
        out = sh("exec-out", "uiautomator", "dump", "/dev/tty")
        m = re.search(r"<\?xml.*</hierarchy>", out, re.S)
        if m:
            return m.group(0)
        time.sleep(1.0)
    sys.exit("uiautomator dump failed after retries (screen busy?) — try `hd shot` fallback")

BOUNDS_RE = re.compile(r"\[(-?\d+),(-?\d+)\]\[(-?\d+),(-?\d+)\]")

def parse(xml_text):
    nodes, size = [], None
    root = ET.fromstring(xml_text)
    def walk(el, depth):
        nonlocal size
        a = el.attrib
        b = BOUNDS_RE.match(a.get("bounds", "")) if a.get("bounds") else None
        if b:
            x1, y1, x2, y2 = map(int, b.groups())
            if size is None:
                size = (x2, y2)
            visible = x2 > x1 and y2 > y1
            node = {
                "depth": depth, "class": a.get("class", "").split(".")[-1],
                "text": a.get("text", ""), "desc": a.get("content-desc", ""),
                "id": (a.get("resource-id", "") or "").split("/")[-1],
                "clickable": a.get("clickable") == "true",
                "focused": a.get("focused") == "true",
                "password": a.get("password") == "true",
                "editable": a.get("class", "").endswith("EditText") or a.get("focusable") == "true" and a.get("class", "").endswith(("EditText", "AutoCompleteTextView")),
                "checked": a.get("checked"), "checkable": a.get("checkable") == "true",
                "selected": a.get("selected"),
                "enabled": a.get("enabled"), "scrollable": a.get("scrollable") == "true",
                "cx": (x1 + x2) // 2, "cy": (y1 + y2) // 2, "bounds": [x1, y1, x2, y2],
            }
            if visible:
                nodes.append(node)
        for c in el:
            walk(c, depth + 1)
    walk(root, 0)
    return nodes, size

def is_informative(n):
    # F1/F7: keep anything actionable OR labeled OR stateful; drop pure layout containers
    return (n["clickable"] or n["scrollable"] or n["text"] or n["desc"]
            or n["checkable"] or n["checked"] == "true" or n["selected"] == "true"
            or n["class"] in ("EditText", "Switch", "CheckBox", "RadioButton", "SeekBar"))

def adopt_labels(nodes):
    # Compose: clickable-but-unlabeled Views adopt the nearest labeled node's text as a hint
    labeled = [n for n in nodes if n["text"] or n["desc"]]
    for n in nodes:
        if n["clickable"] and not n["text"] and not n["desc"]:
            best, bd = None, 1e9
            for l in labeled:
                d = abs(l["cx"] - n["cx"]) + abs(l["cy"] - n["cy"])
                if d < bd:
                    best, bd = l, d
            if best and bd < 400:
                n["hint"] = (best["text"] or best["desc"])[:40]
    return nodes

TOGGLE_CLASSES = ("Switch", "CheckBox", "RadioButton", "ToggleButton")


def render(nodes, full, profile="views"):
    if profile == "compose":
        nodes = adopt_labels(nodes)
        for n in nodes:
            n["text"] = n["text"].replace("&amp;", "&")
            n["desc"] = n["desc"].replace("&amp;", "&")
    shown = nodes if full else [n for n in nodes if is_informative(n)]
    lines = []
    for i, n in enumerate(shown):
        label = n["text"] or n["desc"]
        parts = [f"[{i}]", n["class"] or "node"]
        if label:
            parts.append(json.dumps(label if len(label) <= 80 else label[:77] + "..."))
        if n["id"]:
            parts.append(f"#{n['id']}")
        # F2. Toggle state comes from the node's own attributes, not its class: Compose renders
        # every switch as a bare `View` with checkable="true", so keying off Switch/CheckBox
        # made toggle state invisible in exactly the profile that has no labels to read it from.
        if n["checked"] in ("true", "false") and (
                n["checkable"] or n["class"] in TOGGLE_CLASSES):
            parts.append(f"checked={n['checked']}")
        if n["selected"] in ("true", "false") and n["class"] in TOGGLE_CLASSES:
            parts.append(f"selected={n['selected']}")
        if n.get("hint"):
            parts.append(f"near:{json.dumps(n['hint'])}")
        if n["enabled"] == "false":
            parts.append("disabled")
        flags = "".join(c for c, f in (("C", n["clickable"]), ("S", n["scrollable"]), ("E", n["class"] == "EditText")) if f)
        if flags:
            parts.append(f"<{flags}>")
        parts.append(f"({n['cx']},{n['cy']})")
        lines.append("  " * min(n["depth"], 6) + " ".join(parts))
    return shown, lines

def identity(line):
    """A node line without its index, so an inserted row does not mark everything below it new."""
    return re.sub(r"^(\s*)\[\d+\]\s", r"\1", line)


COORDS = re.compile(r"\s*\((\d+),(\d+)\)\s*$")
INDEX = re.compile(r"^\s*\[(\d+)\]")


def placeless(line):
    """Identity without the node's position: a row that only scrolled is the same row.

    Every rendered line ends in the node's centre `(x,y)`, so keying identity off the whole line
    made a list that scrolled by one row report every row as removed AND re-added — a delta twice
    the size of the tree, which `see` then discards for the whole tree. That is what the
    2026-08-13 A/B/C measured: 1,024 of the 1,287 hybrid re-observations printed
    "changed too much to diff", i.e. the diff was almost never the thing that got printed.
    """
    return COORDS.sub("", identity(line))


def node_index(line):
    m = INDEX.search(line)
    return m.group(1) if m else "?"


def coords(line):
    m = COORDS.search(line)
    return m.group(0).strip() if m else ""


def move_line(old, new):
    """A node the caller has already read, at a new index and/or position — one short line.

    The caller has the old line in its context, so the only news is where the node went. Naming
    it by its OLD index is what makes the new index usable: `hd tap` resolves against the tree
    `see` just cached, so a printed renumbering keeps a scrolled row tappable without reprinting
    it.
    """
    oi, ni = node_index(old), node_index(new)
    return f"~ [{oi}]->[{ni}] {coords(new)}" if oi != ni else f"~ [{ni}] {coords(new)}"


def diff_lines(old, new):
    """(added lines with their current indexes, removed lines, (old, new) pairs that moved).

    Deliberately set-based rather than a sequence diff: what an agent needs after a tap is
    "what is on screen now that was not before", and a scrolled list would otherwise report
    every row as moved. Matching ignores index and position, so a row that merely slid up the
    screen is reported as a renumbering rather than as a removal plus an addition.
    """
    buckets = collections.defaultdict(collections.deque)
    for l in old:
        buckets[placeless(l)].append(l)
    added, moved = [], []
    for l in new:
        q = buckets.get(placeless(l))
        if q:
            o = q.popleft()
            if node_index(o) != node_index(l) or coords(o) != coords(l):
                moved.append((o, l))
        else:
            added.append(l)
    removed = [l.strip() for q in buckets.values() for l in q]
    return added, removed, moved


def informative_mask(shown):
    """Which lines of a FULL rendering a compact one would have kept, positionally."""
    return [is_informative(n) for n in shown]


def print_short(lines, mask, why):
    """Print a full rendering trimmed to its informative lines, keeping their indexes.

    Both misses — `hd see --find PAT` and `hd find PAT` — answer with the tree the caller was
    otherwise going to spend a turn asking for. Both render FULL, because a pattern has to be
    matched against every node, so the short form has to be a SUBSET of that rendering: a
    compact re-render numbers from zero over a different node set, and `hd tap` resolves the
    index against the cached full one. `hd tap 4` off such a tree tapped a FrameLayout at the
    screen's centre instead of the ImageButton printed beside the 4.

    No baseline is recorded: what is printed is neither of the two renderings `see` diffs
    against, so leaving the baseline alone only makes the next `see` print more — never claim
    "no change" about a screen the caller has not read.
    """
    short = [ln for ln, keep in zip(lines, mask) if keep]
    escalated = len(short) < COMPACT_MIN_NODES        # the same floor a compact `see` escalates on
    if escalated:
        short = list(lines)
    print(f"# {why} — showing the {'full' if escalated else 'compact'} tree "
          f"({len(short)} of {len(lines)} nodes, indexes are `hd tap`-able) "
          "so this costs one look, not two")
    print("\n".join(short))


def see(full=False, find=None, diff=True, quiet=False):
    nodes, size = parse(dump_xml())
    profile, src = detect_profile(nodes)
    if find or quiet:
        # Match against everything; indexes must stay valid for `hd tap`. Quiet capture prints
        # nothing, so caching the full tree costs no context and gives `hd find` the better recall.
        full = True
    shown, lines = render(nodes, full, profile)
    if not full and len(shown) < COMPACT_MIN_NODES:  # F7
        shown, lines = render(nodes, True, profile)
        print(f"# compact view had <{COMPACT_MIN_NODES} nodes; auto-escalated to --full")
    mode = "find" if find else "full" if full else "compact"
    kind = "full" if full else "compact"
    st = json.load(open(STATE)) if os.path.exists(STATE) else {}
    now = time.time()
    # Baselines are kept per RENDERING, not per verb. `--find` and `-q` render the full tree, so
    # keying the baseline off the verb meant a `--find` in between two `see`s left nothing a
    # compact `see` could diff against: 49% of the plain re-observations in the 2026-08-10 run
    # followed a `--find`, and every one of them printed a whole tree.
    base = st.get("baselines", {}).get(kind) if diff and not quiet else None
    # Stale either way: by its own capture time, or by the last observation of any kind, which
    # is never older than it.
    if base and max(now - base.get("ts", 0), now - st.get("ts", 0)) > DIFF_MAX_AGE:
        base = None  # too old to be the screen you think it is
    baselines = {k: v for k, v in st.get("baselines", {}).items()
                 if now - v.get("ts", 0) <= DIFF_MAX_AGE}
    # A baseline is only what the CALLER WAS SHOWN. `--find` prints matching lines and `-q`
    # prints nothing, so recording their tree would make the next `see` diff the screen against
    # a tree nobody read: after `tap; see --find X; see` the delta is empty and the answer is
    # "no change since the last see" about a screen the caller has never seen. A rendering that
    # was not printed leaves the previous baseline in place, so the next `see` reports the
    # change since the last tree that actually reached the caller (or re-renders once it ages
    # out).
    if not quiet and not find:
        baselines[kind] = {"lines": lines, "ts": now}
        if full:
            # A printed full render also shows what the compact view of this screen is, and it
            # costs nothing to remember: no extra dump, one format pass over parsed nodes.
            baselines["compact"] = {"lines": render(nodes, False, profile)[1], "ts": now}
    json.dump({"nodes": shown, "ts": now, "lines": lines, "mode": mode,
               "size": list(size), "profile": profile, "baselines": baselines,
               # Which of the cached lines a compact view would have kept, so `hd find` can
               # answer a miss with a short tree. Stored as a mask over `lines` rather than a
               # second rendering because a compact render re-numbers from zero, and every
               # index printed has to address `nodes` — an index that taps a different node
               # than the one beside it is worse than an expensive look.
               "informative": informative_mask(shown)}, open(STATE, "w"))
    if quiet:
        # Capture without printing: the tree is on disk, and `hd find PAT` reads it from there.
        # Costs one line of context instead of the whole screen, for the common case where you
        # know what you are looking for.
        print(f"# screen {size[0]}x{size[1]}, {len(shown)} nodes cached (profile={profile}) "
              f"— `hd find PAT` to read it, `hd see` to print it")
        return
    # Only diff against a tree rendered the same way. A compact tree against a --full one
    # reports every layout container as removed, which is noise, not a change.
    if diff and not find and base and base.get("lines"):
        added, removed, moved = diff_lines(base["lines"], lines)
        out = ([f"+ {l}" for l in added] + [f"- {l}" for l in removed]
               + [move_line(o, n) for o, n in moved])
        # Emit whichever is genuinely cheaper. On a screen that turned over, the delta is the
        # old tree plus the new one, so a diff would be the more expensive way to say it.
        if len("\n".join(out)) < len("\n".join(lines)):
            # Indexes below are the CURRENT ones, so `hd tap` works straight off a diff.
            # Deliberately does NOT name the escape hatch. In the 2026-08-10 run agents typed
            # `hd see --no-diff` 717 times against 15 deltas actually printed — an opt-out
            # advertised on every delta and in the verb list is an opt-out that gets typed.
            # The legend for `~` is printed only when something moved: a header that explains a
            # notation the delta does not use is pure overhead on the small deltas this verb
            # exists for.
            moves = f" ~{len(moved)}" if moved else ""
            legend = ("; `~ [was]->[now] (x,y)` is a node you have read, renumbered"
                      if moved else "")
            print(f"# screen {size[0]}x{size[1]}, +{len(added)} -{len(removed)}{moves} "
                  f"of {len(shown)} nodes (diff vs last see, profile={profile}{legend}; "
                  f"unlisted nodes are unchanged and keep their indexes)")
            print("\n".join(out) if out else "# no change since the last see")
            return
        print("# screen changed too much to diff — showing the whole tree")
    if find:
        pat = re.compile(find, re.I)
        hits = [ln for ln in lines if pat.search(ln)]  # matches labels/ids/class/near-hints/checked= state
        print(f"# screen {size[0]}x{size[1]}, {len(hits)}/{len(shown)} nodes match {find!r} (profile={profile})")
        if hits:
            print("\n".join(hits))
            return
        # A miss tells the caller nothing about the screen, so it used to end with "re-run
        # without --find" — an instruction that costs a whole extra turn to obey, and one the
        # caller obeyed 40 times over the 12 hybrid runs of the 2026-08-11 matrix. Print the
        # tree it was about to ask for instead, exactly as the <5-node case already escalates.
        # `--find` renders FULL (indexes must address every node), so the short version is that
        # rendering minus its uninformative lines — NOT a compact re-render, whose indexes
        # count from zero over a different node set and would tap the wrong node.
        print_short(lines, informative_mask(shown), "NO MATCH")
        return
    print(f"# screen {size[0]}x{size[1]}, {len(shown)} nodes ({'full' if full else 'compact'}, profile={profile} {src})")
    if profile == "views" and not full and len(shown) > 25:
        print("# TIP (views profile): this tree is labeled — `hd see --find PAT` is much cheaper when you know the target")
    print("\n".join(lines))

def load_state():
    if not os.path.exists(STATE):
        sys.exit("no previous `hd see` — observe first")
    return json.load(open(STATE))


def find_cached(pat):
    """Grep the cached tree. Re-dumps only if the cache is too old to trust (DIFF_MAX_AGE).

    This is the retrieval half of `hd see -q`: capture puts the screen on disk for free, and
    only the matching lines are ever printed into the context.
    """
    st = json.load(open(STATE)) if os.path.exists(STATE) else None
    if not st or time.time() - st.get("ts", 0) > DIFF_MAX_AGE:
        return see(find=pat)
    rx = re.compile(pat, re.I)
    hits = [ln for ln in st["lines"] if rx.search(ln)]
    w, h = st.get("size", (0, 0))
    age = int(time.time() - st["ts"])
    print(f"# screen {w}x{h}, {len(hits)}/{len(st['lines'])} nodes match {pat!r} "
          f"(cached {age}s ago, profile={st.get('profile')})")
    if hits:
        print("\n".join(hits))
        return
    # A miss used to end by asking for a re-observation before concluding the node absent: a turn
    # spent fetching a tree this verb is already holding (the cache is inside DIFF_MAX_AGE by
    # the branch above), which is what `hd see --find` stopped doing in #11.
    print_short(st["lines"], st.get("informative") or [], f"NO MATCH in the cache ({age}s old)")

def tap(index, long=False):
    st = load_state()
    if time.time() - st["ts"] > 120:
        sys.exit("last `see` is >120s old — re-observe first (F8)")
    try:
        n = st["nodes"][index]
    except IndexError:
        sys.exit(f"index {index} out of range (0..{len(st['nodes'])-1})")
    # F4/F8: re-dump and verify the node hasn't moved. Only re-match nodes with a
    # distinguishing label/id — unlabeled nodes would fuzzy-match the wrong sibling.
    if n["text"] or n["desc"] or n["id"]:
        fresh, _ = parse(dump_xml())
        same = [f for f in fresh if f["class"] == n["class"] and f["text"] == n["text"]
                and f["desc"] == n["desc"] and f["id"] == n["id"]]
        # "Has a label or an id" is not the same as "is identifiable by it". A form's fields
        # share one id and are all empty (`#text-input-outlined` x3 in LessPass), so the first
        # match is a SIBLING, and following it tapped the row above the one the caller indexed
        # — silently, under a message saying the node had moved. When the identity is ambiguous,
        # the index the caller gave is the only thing that distinguishes the node, so keep the
        # coordinates that came with it.
        match = same[0] if len(same) == 1 else None
        if match and (abs(match["cx"] - n["cx"]) > 40 or abs(match["cy"] - n["cy"]) > 40):
            n = match
            print(f"# node moved; tapping fresh coords ({n['cx']},{n['cy']})")
        elif not same:
            sys.exit("node no longer on screen — re-observe with `hd see`")
    if long:
        sh("shell", "input", "swipe", str(n["cx"]), str(n["cy"]), str(n["cx"]), str(n["cy"]), "800")
    else:
        sh("shell", "input", "tap", str(n["cx"]), str(n["cy"]))
    print(f"{'long-pressed' if long else 'tapped'} [{index}] {n['class']} {json.dumps(n['text'] or n['desc'])} at ({n['cx']},{n['cy']})")

KEYS = {"back": "4", "home": "3", "enter": "66", "tab": "61", "delete": "67", "appswitch": "187"}
MOVE_END, DEL = "123", "67"
CLEAR_CAP = 200  # a field whose text the tree withholds (password) still has to terminate


def clear_focused():
    """Empty the focused text field. Returns what was in it.

    The character count comes from the tree, not from the caller: `input keyevent` has no
    select-all that survives every IME, so a replacement is a MOVE_END plus one DEL per
    character, and the only question is how many. Agents that had to guess got it wrong in both
    directions — in the 2026-08-12 A/B/C the hybrid arm hand-rolled 28 backspace loops over 8 of
    its 12 runs, 405 keyevents, re-guessing 20 -> 30 -> 40 on the same field — and each wrong
    guess costs a turn plus the look that reveals the residue. hd already holds the field's
    text, so it can send the exact count, in one `input keyevent` call rather than one per
    character.
    """
    nodes, _ = parse(dump_xml())
    field = next((n for n in nodes if n["focused"] and (n["editable"] or n["class"] == "EditText")), None)
    if field is None:
        sys.exit("no focused text field — tap the field first (`hd tap <index> -n; hd type ... -r`)")
    old = field["text"]
    # An empty field needs no deletion — except a password one, which some IMEs render as an
    # empty string rather than a bullet per character; there, delete a bounded worst case rather
    # than reporting success over text that is still in the field.
    count = len(old) if old else CLEAR_CAP if field["password"] else 0
    if not count:
        return old
    sh("shell", "input", "keyevent", MOVE_END, *([DEL] * count))
    return old

def screen_size():
    out = sh("shell", "wm", "size")
    m = re.search(r"Override size:\s*(\d+)x(\d+)", out) or re.search(r"Physical size:\s*(\d+)x(\d+)", out)
    return (int(m.group(1)), int(m.group(2))) if m else (1080, 2400)

def wait_idle(timeout=5.0):
    """Block until the focused window stops changing, or `timeout`. Prints nothing."""
    end = time.time() + timeout
    prev = None
    while time.time() < end:
        cur = sh("shell", "dumpsys", "window", "|", "grep", "-E", "mCurrentFocus")
        if cur == prev:
            return True
        prev = cur
        time.sleep(0.5)
    return False


ACTIONS = {"tap", "tap-xy", "longpress", "longpress-xy", "type", "key", "swipe", "clear"}


def see_flag(a):
    """(observe after the action?, optional --find pattern, was it asked for explicitly?).

    Folding the observation into the action is the whole point: an agent that types `hd tap 5`
    and then `hd see` pays for two turns to learn one thing. `-s` shipped as opt-in and was
    typed on 312 of 1,569 actions (20%) in the 2026-08-11 A/B/C, which is why that run still
    spent 3.26 looks per task against an unaided agent's 1.96 and 1.10x its ACU at 0.67x its
    perception tokens. A saving nobody types is not a saving, so the fold is the default and
    `-n`/`--no-see` opts out — the flag a batch wants on all but its last action.
    """
    if "-n" in a or "--no-see" in a:
        return False, None, True
    for f in ("-s", "--see"):
        if f in a:
            i = a.index(f)
            nxt = a[i + 1] if len(a) > i + 1 else None
            return True, (nxt if nxt and not nxt.startswith("-") else None), True
    return True, None, False


def hint_no_see():
    """Name the opt-out once per session, not on every action.

    An opt-out advertised nowhere is `--no-diff`: never typed. One advertised on every delta is
    `--no-diff` after it was advertised: typed 717 times against 15 deltas actually printed.
    Once is enough to be discoverable and costs one line a session. Kept out of STATE, which
    `see` rewrites wholesale on every observation.
    """
    if os.path.exists(HINTED):
        return
    print("# (an action observes after itself; `-n` skips that look — use it on every action of "
          "a batch but the last)")
    open(HINTED, "w").close()


def main():
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    cmd = a[0]
    # `hd type "-n"` types a literal `-n`, so flags are read past each verb's own operands.
    flags = a[{"type": 2, "tap-xy": 3, "longpress-xy": 3, "clear": 1}.get(cmd, 2):]
    observe, pattern, explicit = see_flag(flags) if cmd in ACTIONS else (False, None, True)
    if cmd == "see":
        find = a[a.index("--find") + 1] if "--find" in a else None
        see(full="--full" in a, find=find, diff="--no-diff" not in a,
            quiet="-q" in a or "--quiet" in a)
    elif cmd == "find":
        find_cached(a[1])
    elif cmd == "tap":
        tap(int(a[1]))
    elif cmd == "longpress":
        tap(int(a[1]), long=True)
    elif cmd == "tap-xy":
        sh("shell", "input", "tap", a[1], a[2]); print(f"tapped ({a[1]},{a[2]})")
    elif cmd == "longpress-xy":
        sh("shell", "input", "swipe", a[1], a[2], a[1], a[2], "800"); print(f"long-pressed ({a[1]},{a[2]})")
    elif cmd == "clear":
        print(f"cleared {clear_focused()!r}")
    elif cmd == "type":
        if "-r" in flags or "--replace" in flags:
            print(f"cleared {clear_focused()!r}")
        # `adb shell` concatenates its arguments and runs them through the device shell, so the
        # text has to survive that shell: quote it, and keep %s for spaces (input text splits on
        # them). Without quoting, any of ()&;<>|'"$` aborts the command with a syntax error.
        sh("shell", "input", "text", shlex.quote(a[1].replace(" ", "%s")))
        print(f"typed {a[1]!r}")
    elif cmd == "key":
        sh("shell", "input", "keyevent", KEYS.get(a[1], a[1])); print(f"key {a[1]}")
    elif cmd == "swipe":
        d = a[1]; steps = 300
        # Scale to the real display: fixed 1080x2400 coordinates fall off the bottom of any
        # shorter screen, where the swipe silently does nothing.
        w, h = screen_size()
        lo_y, hi_y = int(h * 0.30), int(h * 0.70)
        lo_x, hi_x = int(w * 0.20), int(w * 0.80)
        coords = {"up": (w // 2, hi_y, w // 2, lo_y), "down": (w // 2, lo_y, w // 2, hi_y),
                  "left": (hi_x, h // 2, lo_x, h // 2), "right": (lo_x, h // 2, hi_x, h // 2)}[d]
        sh("shell", "input", "swipe", *map(str, coords), str(steps)); print(f"swiped {d}")
    elif cmd == "shot":
        open(a[1], "wb").write(sh("exec-out", "screencap", "-p", binary=True))
        print(f"screenshot -> {a[1]}")
    elif cmd == "wait-idle":
        timeout = float(a[a.index("--timeout") + 1]) if "--timeout" in a else 5.0
        print("idle" if wait_idle(timeout) else "timeout (proceeding)")
    else:
        sys.exit(f"unknown verb {cmd!r}\n{__doc__}")
    if observe:
        if not explicit:
            hint_no_see()
        wait_idle(3.0)
        see(find=pattern)

if __name__ == "__main__":
    main()
