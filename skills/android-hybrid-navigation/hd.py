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
React Native), detected once per app and cached. Override with HD_PROFILE=views|compose|rn.
Action: coordinate taps/swipes/keys via `adb shell input` (never a11y performAction).
Text: `adb shell input text` (injects below the IME — host-keyboard-proof).
Screenshots: explicit `shot` verb only.

Verbs:
  hd see [--full] [--find PAT]   observe screen; --find prints ONLY nodes matching regex PAT
                                  (case-insensitive, over label/id/class) plus their index —
                                  the cheapest observation when you know what you're looking for
  hd tap <index>         tap center of node <index> from the LAST `see` (re-verifies first)
  hd tap-xy <x> <y>      raw coordinate tap
  hd longpress <index>   long-press node <index> — THE way to open an item's context menu
                         (rename/delete/copy on list items and files). Try this FIRST when a
                         per-item action has no visible button.
  hd longpress-xy <x> <y>  raw coordinate long-press
  hd type "text"         type into the focused field
  hd key <name>          back|home|enter|tab|delete or raw keycode number
  hd swipe up|down|left|right [--steps N]
  hd shot <file.png>     screenshot to file
  hd wait-idle [--timeout S]
State file: /tmp/hd_last_tree.json (indexes are only valid against the last `see`).
"""
import json, os, re, subprocess, sys, time
import xml.etree.ElementTree as ET

ADB = os.environ.get("HD_ADB", "adb")
STATE = "/tmp/hd_last_tree.json"
FW_CACHE = "/tmp/hd_fw_cache.json"
COMPACT_MIN_NODES = 5  # F7: auto-escalate below this

def foreground_pkg():
    out = sh("shell", "dumpsys", "window")
    m = re.search(r"mCurrentFocus=.*?\s([\w.]+)/", out)
    return m.group(1) if m else None

def detect_profile(nodes):
    forced = os.environ.get("HD_PROFILE")
    if forced:
        return forced, "(forced)"
    if any(n["class"] == "ComposeView" for n in nodes):
        return "compose", "(ComposeView in tree)"
    pkg = foreground_pkg()
    if not pkg:
        return "views", "(unknown pkg)"
    cache = json.load(open(FW_CACHE)) if os.path.exists(FW_CACHE) else {}
    if pkg not in cache:
        path_out = sh("shell", "pm", "path", pkg)
        apks = [l.split(":", 1)[1].strip() for l in path_out.splitlines() if l.startswith("package:")]
        prof = "views"
        for apk in apks:
            r = subprocess.run([ADB, "shell", f"grep -qm1 libreactnative {apk} 2>/dev/null"])
            if r.returncode == 0:
                prof = "rn"; break
        cache[pkg] = prof
        json.dump(cache, open(FW_CACHE, "w"))
    return cache[pkg], pkg

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
        for attr in ("checked", "selected"):
            if n[attr] in ("true", "false") and n["class"] in ("Switch", "CheckBox", "RadioButton", "ToggleButton"):
                parts.append(f"{attr}={n[attr]}")  # F2
        if profile == "rn" and n.get("checkable") and "checked=" not in " ".join(parts):
            parts.append(f"checked={n['checked']}")
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

def see(full=False, find=None):
    nodes, size = parse(dump_xml())
    profile, src = detect_profile(nodes)
    if find:
        full = True  # match against everything; indexes must stay valid for `hd tap`
    shown, lines = render(nodes, full, profile)
    if not full and len(shown) < COMPACT_MIN_NODES:  # F7
        shown, lines = render(nodes, True, profile)
        print(f"# compact view had <{COMPACT_MIN_NODES} nodes; auto-escalated to --full")
    json.dump({"nodes": shown, "ts": time.time()}, open(STATE, "w"))
    if find:
        pat = re.compile(find, re.I)
        hits = [ln for ln in lines if pat.search(ln)]  # matches labels/ids/class/near-hints/checked= state
        print(f"# screen {size[0]}x{size[1]}, {len(hits)}/{len(shown)} nodes match {find!r} (profile={profile})")
        print("\n".join(hits) if hits else "# NO MATCH — re-run without --find (or --full) before concluding it's absent")
        return
    print(f"# screen {size[0]}x{size[1]}, {len(shown)} nodes ({'full' if full else 'compact'}, profile={profile} {src})")
    if profile == "views" and not full and len(shown) > 25:
        print("# TIP (views profile): this tree is labeled — `hd see --find PAT` is much cheaper when you know the target")
    print("\n".join(lines))

def load_state():
    if not os.path.exists(STATE):
        sys.exit("no previous `hd see` — observe first")
    return json.load(open(STATE))

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
        match = next((f for f in fresh if f["class"] == n["class"] and f["text"] == n["text"]
                      and f["desc"] == n["desc"] and f["id"] == n["id"]), None)
        if match and (abs(match["cx"] - n["cx"]) > 40 or abs(match["cy"] - n["cy"]) > 40):
            n = match
            print(f"# node moved; tapping fresh coords ({n['cx']},{n['cy']})")
        elif match is None:
            sys.exit("node no longer on screen — re-observe with `hd see`")
    if long:
        sh("shell", "input", "swipe", str(n["cx"]), str(n["cy"]), str(n["cx"]), str(n["cy"]), "800")
    else:
        sh("shell", "input", "tap", str(n["cx"]), str(n["cy"]))
    print(f"{'long-pressed' if long else 'tapped'} [{index}] {n['class']} {json.dumps(n['text'] or n['desc'])} at ({n['cx']},{n['cy']})")

KEYS = {"back": "4", "home": "3", "enter": "66", "tab": "61", "delete": "67", "appswitch": "187"}

def main():
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    cmd = a[0]
    if cmd == "see":
        find = a[a.index("--find") + 1] if "--find" in a else None
        see(full="--full" in a, find=find)
    elif cmd == "tap":
        tap(int(a[1]))
    elif cmd == "longpress":
        tap(int(a[1]), long=True)
    elif cmd == "tap-xy":
        sh("shell", "input", "tap", a[1], a[2]); print(f"tapped ({a[1]},{a[2]})")
    elif cmd == "longpress-xy":
        sh("shell", "input", "swipe", a[1], a[2], a[1], a[2], "800"); print(f"long-pressed ({a[1]},{a[2]})")
    elif cmd == "type":
        text = a[1].replace(" ", "%s")
        sh("shell", "input", "text", text); print(f"typed {a[1]!r}")
    elif cmd == "key":
        sh("shell", "input", "keyevent", KEYS.get(a[1], a[1])); print(f"key {a[1]}")
    elif cmd == "swipe":
        d = a[1]; steps = 300
        coords = {"up": (540, 1600, 540, 700), "down": (540, 700, 540, 1600),
                  "left": (900, 1200, 200, 1200), "right": (200, 1200, 900, 1200)}[d]
        sh("shell", "input", "swipe", *map(str, coords), str(steps)); print(f"swiped {d}")
    elif cmd == "shot":
        open(a[1], "wb").write(sh("exec-out", "screencap", "-p", binary=True))
        print(f"screenshot -> {a[1]}")
    elif cmd == "wait-idle":
        timeout = float(a[a.index("--timeout") + 1]) if "--timeout" in a else 5.0
        end = time.time() + timeout
        prev = None
        while time.time() < end:
            cur = sh("shell", "dumpsys", "window", "|", "grep", "-E", "mCurrentFocus")
            if cur == prev:
                print("idle"); return
            prev = cur; time.sleep(0.5)
        print("timeout (proceeding)")
    else:
        sys.exit(f"unknown verb {cmd!r}\n{__doc__}")

if __name__ == "__main__":
    main()
