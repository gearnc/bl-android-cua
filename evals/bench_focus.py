"""Bench: what it costs to find out WHICH field the text verbs will type into.

`hd type`, `hd type -r` and `hd clear` all act on the focused field and nothing else, but the
tree rendered every state except that one, and the failure named no node:

    $ hd type "new" -r
    no focused text field — tap the field first (`hd tap <index> -n; hd type ... -r`)

so recovering meant buying a look the agent had just paid for. The 36-run 2026-08-14 A/B/C
measured 70 focus-hunting commands (`hd see --full | grep -i edit`, `hd see --find EditText`,
`keyevent 123`) across 10 of the 12 hybrid runs, 46 of them in the four Compose cells — the
stack where hybrid spent 1.22x bare's perception tokens (seal 1.57x), and the same runs that
still hand-rolled backspace loops after `-r` refused.

Per app it checks the two halves of the fix and the regression it must not cause:

  * `focus`  — the tree marks the focused field `<F>`, and marks exactly the node the
    UIAutomator dump says is focused, so a look can answer the text verbs' precondition;
  * `failure` — on a screen with fields but nothing focused, `hd type -r` names the indexes
    that focus one, priced against the `hd see --full` the old revision leaves the agent
    needing (what the eval's hybrid runs typed next);
  * `replace` — with a field focused, `-r` still deletes exactly the field's contents.

Apps differ in which halves they can exercise: an app that opens with its field already
focused (React Native ones do) cannot show the failure, and reports `n/a` for it.

Usage:  python3 evals/bench_focus.py [app ...]
        HD_PY_OLD=/path/to/old/hd.py  (default: this file's revision as of git HEAD)
"""

import os
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from env import ADB, ENV, find_hd  # noqa: E402
from suites import APPS  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
DEFAULT = ("seal", "lesspass")
EDIT = re.compile(r"<[CSEF]*E[CSEF]*>")
FOCUS = re.compile(r"<[CSEF]*F[CSEF]*>")
DISMISS = re.compile(r'"(Close|Got it|Skip|Dismiss|OK|Accept)"')


def hd(path, *args):
    r = subprocess.run(["python3", path, *args], capture_output=True, text=True, env=ENV)
    return r.stdout + r.stderr


def adb(*args):
    return subprocess.run([ADB, *args], capture_output=True, text=True, env=ENV).stdout


def tree(path):
    """A full rendering with no delta.

    Both revisions share one state file, so a diffed look would show one revision the other's
    baseline — and the flag under test would arrive as a delta line rather than a rendering.
    """
    return hd(path, "see", "--full", "--no-diff")


def old_revision():
    """The pre-fix `hd.py`, so the bench compares two revisions and not two flags."""
    if os.environ.get("HD_PY_OLD"):
        return os.environ["HD_PY_OLD"]
    out = subprocess.run(["git", "show", "HEAD:skills/android-hybrid-navigation/hd.py"],
                         cwd=REPO, capture_output=True, text=True)
    if out.returncode:
        sys.exit("no HD_PY_OLD and `git show HEAD:...hd.py` failed")
    p = Path("/tmp/hd_old_focus.py")
    p.write_text(out.stdout)
    return str(p)


def index_of(line):
    return line.strip()[1:line.strip().index("]")]


def editable(rendering):
    return [ln.strip() for ln in rendering.splitlines() if EDIT.search(ln)]


def focused(rendering):
    return [ln.strip() for ln in rendering.splitlines() if FOCUS.search(ln)]


def dump_focus():
    """What the platform says is focused: the truth `<F>` has to agree with."""
    adb("shell", "uiautomator", "dump", "/sdcard/hd_bench.xml")
    xml = adb("shell", "cat", "/sdcard/hd_bench.xml")
    return [m for m in re.findall(r'<node[^>]*focused="true"[^>]*/?>', xml)]


def bounds_of(line):
    m = re.search(r"\((\d+),(\d+)\)$", line)
    return (int(m.group(1)), int(m.group(2))) if m else None


def marks_the_focused_node(rendering):
    """`<F>` names the node the dump calls focused, and does not name a second one."""
    marked = focused(rendering)
    if len(marked) != 1:
        return len(marked) == len(dump_focus()) == 0
    cx, cy = bounds_of(marked[0]) or (None, None)
    for node in dump_focus():
        b = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', node)
        if b and abs((int(b.group(1)) + int(b.group(3))) // 2 - cx) <= 2 \
                and abs((int(b.group(2)) + int(b.group(4))) // 2 - cy) <= 2:
            return True
    return False


def open_app(new, app):
    """Launch, and dismiss a first-run card if one stands between us and the app."""
    adb("shell", "am", "force-stop", APPS[app]["pkg"])
    adb("shell", "monkey", "-p", APPS[app]["pkg"], "-c", "android.intent.category.LAUNCHER", "1")
    time.sleep(6)
    for _ in range(2):
        rendering = tree(new)
        if editable(rendering):
            return rendering
        # The tappable node, not the label beside it: Compose renders the button as an
        # unlabeled `View <C>` that adopts the TextView's text as a `near:` hint.
        card = next((ln for ln in rendering.splitlines()
                     if ln.strip().startswith("[") and DISMISS.search(ln) and "<C" in ln), None)
        if not card:
            break
        hd(new, "tap", index_of(card), "-n")
        time.sleep(3)
    return tree(new)


def measure(old, new, app):
    rendering = open_app(new, app)
    fields = editable(rendering)
    if not fields:
        return None
    row = {"app": app, "fields": len(fields), "honest": marks_the_focused_node(rendering)}
    if not focused(rendering):
        # The failure under test. Neither revision touches the device when it fires, so the two
        # can be priced back to back on one screen.
        fail_old, fail_new = hd(old, "type", "bench", "-r"), hd(new, "type", "bench", "-r")
        row.update(fail_old=len(fail_old), fail_new=len(fail_new),
                   named_old=bool(re.search(r"\[\d+\]", fail_old)),
                   named_new=bool(re.search(r"\[\d+\]", fail_new)),
                   recovery=len(tree(old)))
        hd(new, "tap", index_of(fields[0]), "-n")
        time.sleep(2)
        rendering = tree(new)
        row["honest"] = row["honest"] and marks_the_focused_node(rendering)
    row["focus_old"] = bool(focused(tree(old)))
    row["focus_new"] = bool(focused(rendering))
    # Regression: with a field focused, `-r` still deletes exactly what was in it.
    hd(new, "clear", "-n")
    hd(new, "type", "hd-bench-value", "-n")
    time.sleep(1)
    hd(new, "type", "replaced", "-r", "-n")
    time.sleep(1)
    got = focused(tree(new))
    row["replaced"] = bool(got) and re.search(r'"((?:[^"\\]|\\.)*)"', got[0]) \
        and re.search(r'"((?:[^"\\]|\\.)*)"', got[0]).group(1) == "replaced"
    hd(new, "clear", "-n")
    return row


def cell(row, key, width, right=True):
    text = str(row[key]) if key in row else "n/a"
    return text.rjust(width) if right else text.ljust(width)


def main(apps):
    old, new = old_revision(), find_hd()
    print(f"old={old}\nnew={new}\n")
    rows = [r for r in (measure(old, new, a) for a in apps) if r]
    if not rows:
        sys.exit("no app exposed a text field — nothing measured")
    print(f"{'app':<10} {'fields':>6} {'unfocused -r, chars':>21} {'names an index':>16} "
          f"{'look it saves':>14} {'<F> old/new':>12} {'honest':>7} {'-r ok':>6}")
    for r in rows:
        print(f"{r['app']:<10} {r['fields']:>6} "
              f"{cell(r, 'fail_old', 9)} ->{cell(r, 'fail_new', 9)} "
              f"{cell(r, 'named_old', 6)}->{cell(r, 'named_new', 8, right=False)} "
              f"{cell(r, 'recovery', 14)} "
              f"{str(r['focus_old']):>5}/{str(r['focus_new']):<6} "
              f"{str(r['honest']):>7} {str(bool(r['replaced'])):>6}")
    priced = [r for r in rows if "recovery" in r]
    if priced:
        saved = sum(r["recovery"] - (r["fail_new"] - r["fail_old"]) for r in priced) / len(priced)
        print(f"\nmean characters the named failure saves per unfocused `-r`: {saved:,.0f} "
              f"(over {len(priced)} of {len(rows)} apps; the rest open already focused)")
    problems = [r["app"] for r in rows
                if not (r["focus_new"] and r["honest"] and r["replaced"])
                or r["focus_old"] or r.get("named_old") or r.get("named_new") is False]
    print("problems:", ", ".join(problems) if problems else "none")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main([a for a in sys.argv[1:] if a in APPS] or list(DEFAULT)))
