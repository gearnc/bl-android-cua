"""Bench: the look-bought-an-index hint has to suggest something a caller would type.

The hint shipped after the 2026-08-15 A/B/C and the 2026-08-16 matrix at `477c380` measured it
again: `hd tap "PAT"` was typed on 1 of 917 taps (0%, down from 126/781), while 147 of the hybrid
arm's 291 look-only commands were still a standalone look followed by nothing but
`hd tap <index>`. The hint fires, so what it prints is the suspect — and it printed the node's
WHOLE label, so on a real screen the one line the caller gets can read

    `hd tap "Notebook is the folder that Markor loads in the file browser when the app is ..."`

which is longer than the tree row it replaces, and, when the label carries regex metacharacters,
is not even quotable: `tap_pattern` compiles the suggestion, so `Save (2)` raises rather than taps.

This bench walks every labelled node of the screen each app opens on and scores the suggestion
each revision would print for it:

  * length     — characters the caller must retype (the whole point of the pattern form);
  * safe       — no regex metacharacter, i.e. executable exactly as printed;
  * truthful   — resolving it the way `tap_pattern` does lands on the same node;
  * coverage   — nodes that get any suggestion at all (silence is correct, but 0% is not a hint).

    python3 evals/bench_hint_pattern.py [app ...]

`$HD_PY` selects the revision under test; `$HD_BASE` (default: `git show HEAD:...hd.py`) is the
revision it is compared against.
"""
import importlib.util
import json
import os
import re
import subprocess
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from env import ADB, ENV, find_hd  # noqa: E402
from test_diff import launch  # noqa: E402

STATE = "/tmp/hd_last_tree.json"
META = re.compile(r"[\\^$.|?*+()\[\]{}]")
CAP = 24


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def base_revision():
    if os.environ.get("HD_BASE"):
        return os.environ["HD_BASE"]
    root = Path(__file__).resolve().parent.parent
    out = subprocess.run(["git", "show", "HEAD:skills/android-hybrid-navigation/hd.py"],
                         cwd=root, capture_output=True, text=True)
    if out.returncode:
        return None
    p = Path("/tmp/hd_base_rev.py")
    p.write_text(out.stdout)
    return str(p)


def screen(pkg):
    """The tree the app opens on, as hd itself cached it."""
    subprocess.run([ADB, "shell", "am", "force-stop", pkg], capture_output=True, env=ENV)
    time.sleep(1)
    launch(pkg)
    subprocess.run(["python3", find_hd(), "see", "--full", "--no-diff"],
                   capture_output=True, env=ENV, text=True)
    return json.load(open(STATE))


def suggestion(mod, st, node):
    """What this revision would print for `node`, without the once-per-session gate."""
    if hasattr(mod, "hint_pattern"):
        return mod.hint_pattern(st, node)
    label = mod.label_of(node)                       # the pre-fix rule, inlined from hint_tap_label
    if not label or not label.isascii() or len(label) < 3:
        return None
    rx = re.compile(re.escape(label), re.I)
    hits = [n for n in st.get("nodes", []) if rx.search(mod.label_of(n))]
    if not all(abs(n["cx"] - node["cx"]) <= 40 and abs(n["cy"] - node["cy"]) <= 40 for n in hits):
        return None
    return label


def resolves_to(st, pat, node):
    """`tap_pattern`'s own resolution: unique hit, or hits that are all one spot."""
    try:
        rx = re.compile(pat, re.I)
    except re.error:
        return False
    hits = [i for i, ln in enumerate(st["lines"]) if rx.search(ln)]
    if not hits:
        return False
    clickable = [i for i in hits if st["nodes"][i].get("clickable")]
    pool = clickable or hits
    first = st["nodes"][pool[0]]
    same = all(abs(st["nodes"][i]["cx"] - first["cx"]) <= 40
               and abs(st["nodes"][i]["cy"] - first["cy"]) <= 40 for i in pool)
    if len(pool) > 1 and not same:
        return False
    return abs(first["cx"] - node["cx"]) <= 40 and abs(first["cy"] - node["cy"]) <= 40


def score(mod, trees):
    lens, fired, unsafe, untruthful, nodes = [], 0, 0, 0, 0
    for st in trees:
        for node in st["nodes"]:
            if not mod.label_of(node):
                continue
            nodes += 1
            pat = suggestion(mod, st, node)
            if not pat:
                continue
            fired += 1
            lens.append(len(pat))
            unsafe += bool(META.search(pat))
            untruthful += not resolves_to(st, pat, node)
    return dict(nodes=nodes, fired=fired, unsafe=unsafe, untruthful=untruthful,
                median=int(statistics.median(lens)) if lens else 0, max=max(lens, default=0),
                over_cap=sum(x > CAP for x in lens))


def show(name, s):
    print(f"{name:<10} fires on {s['fired']:>3}/{s['nodes']:<3} labelled nodes  "
          f"median {s['median']:>3}c  max {s['max']:>4}c  over {CAP}c: {s['over_cap']:>3}  "
          f"unquotable: {s['unsafe']:>2}  wrong node: {s['untruthful']:>2}")


if __name__ == "__main__":
    from suites import APPS  # noqa: E402

    which = sys.argv[1:] or ["markor", "amaze", "seal", "unitto", "joplin", "lesspass"]
    trees = []
    for app in which:
        try:
            trees.append(screen(APPS[app]["pkg"]))
        except Exception as e:                                          # noqa: BLE001
            print(f"{app}: FAILED to capture a tree ({e})")
    assert trees, "no trees captured — is the emulator up?"
    print(f"{sum(len(t['nodes']) for t in trees)} nodes over {len(trees)} app screens\n")

    new = load(find_hd(), "hd_new")
    old_path = base_revision()
    if old_path:
        old = load(old_path, "hd_old")
        before = score(old, trees)
        show("before", before)
    after = score(new, trees)
    show("after", after)

    assert after["fired"], "the hint never fires — every labelled node was rejected"
    assert not after["unsafe"], "suggested a pattern that tap_pattern cannot compile"
    assert not after["untruthful"], "suggested a pattern that resolves to a different node"
    assert not after["over_cap"], f"suggested a pattern longer than {CAP} characters"
    if old_path:
        print(f"\nlongest suggestion {before['max']}c -> {after['max']}c, "
              f"unquotable {before['unsafe']} -> 0, wrong node {before['untruthful']} -> 0")
    print("\nOK")
