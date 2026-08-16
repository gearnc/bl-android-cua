"""Bench + regression: what a look pays for that is not a node.

The 2026-08-16 A/B/C is the first run where the `raw` arm — a 30-line `uiautomator dump`
wrapper and nothing else — undercut `hd` on the price of a single observation: 282 perception
tokens per look against hybrid's 603, on the same suites and the same screens. Two components of
that gap are pure packaging, and this bench prices both against the raw wrapper's rendering of
the identical screen:

  * indentation. `render()` indented every line by its tree depth, clamped at 6. Over the six
    eval apps every informative node clamped, so a tree arrived with a constant 12-space prefix
    on 100% of its lines — 22% of the printed bytes of a look, carrying no structure whatsoever.
    Re-basing on the shallowest shown node keeps relative nesting and drops the constant.
  * the views TIP. It fired on every plain `hd see` of a large labeled tree; the hybrid arm typed
    202 such looks, buying one sentence ~200 times.

Also the regression the first fix needs: where depth genuinely varies below the cap, the relative
nesting must survive the re-basing, or the tree stops saying which rows are children.

    python3 evals/bench_look_overhead.py [app ...]

`$HD_PY` selects the revision under test, so the before/after can be run against two checkouts.
"""
import importlib.util
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from env import ADB, ENV, find_hd  # noqa: E402
from suites import APPS  # noqa: E402

HD = ["python3", find_hd()]
DEFAULT = ("markor", "amaze", "seal", "unitto", "joplin", "lesspass")

# The method the raw arm was handed, verbatim from `skills/android-raw-navigation/SKILL.md`:
# the comparison is only fair if the baseline is the renderer the other arm actually ran.
RAW_WRAPPER = r'''
import re, subprocess, sys
import xml.etree.ElementTree as ET
subprocess.run([sys.argv[1], "shell", "uiautomator", "dump", "/sdcard/ui.xml"],
               capture_output=True)
xml = subprocess.run([sys.argv[1], "shell", "cat", "/sdcard/ui.xml"],
                     capture_output=True, text=True).stdout
for n in ET.fromstring(xml).iter("node"):
    t = n.get("text") or n.get("content-desc")
    if n.get("clickable") != "true" and n.get("scrollable") != "true" and not t:
        continue
    x1, y1, x2, y2 = map(int, re.findall(r"-?\d+", n.get("bounds")))
    print(f'{n.get("class").split(".")[-1]} "{t or ""}" '
          f'{"C" if n.get("clickable") == "true" else ""}'
          f'{"S" if n.get("scrollable") == "true" else ""} '
          f"({(x1 + x2) // 2},{(y1 + y2) // 2})")
'''


def hd(*args):
    return subprocess.run(HD + list(args), capture_output=True, text=True, env=ENV).stdout


def launch(pkg):
    subprocess.run([ADB, "shell", "monkey", "-p", pkg, "-c",
                    "android.intent.category.LAUNCHER", "1"], capture_output=True, env=ENV)
    time.sleep(4)


def raw_look(script):
    return subprocess.run(["python3", script, ADB], capture_output=True, text=True,
                          env=ENV).stdout


def indent_bytes(tree):
    return sum(len(ln) - len(ln.lstrip()) for ln in tree.splitlines() if ln.startswith(" "))


def render_of(hd_py):
    """`render` from the revision under test, so the unit check runs against the real function."""
    spec = importlib.util.spec_from_file_location("hd_under_test", hd_py)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.render


def node(depth, i):
    return dict(depth=depth, **{k: "" for k in ("text", "desc", "id", "checked", "selected")},
                **{k: False for k in ("clickable", "scrollable", "focused", "checkable")},
                **{"class": f"N{i}", "enabled": "true", "cx": i, "cy": i})


def check_relative_nesting():
    """Re-basing may only remove the CONSTANT part of the indentation."""
    render = render_of(find_hd())
    nodes = [node(3, 0), node(4, 1), node(5, 2), node(3, 3)]
    _, lines = render(nodes, full=True)
    pre = [len(ln) - len(ln.lstrip()) for ln in lines]
    ok = pre == [0, 2, 4, 0]
    print(f"\nrelative nesting under a re-based tree: {pre} "
          f"{'(preserved)' if ok else '(BROKEN — expected [0, 2, 4, 0])'}")
    return ok


def main(apps):
    wrapper = Path("/tmp/hd_bench_raw_ui.py")
    wrapper.write_text(RAW_WRAPPER)
    print(f"{'app':10s} {'hd bytes':>9s} {'indent':>7s} {'share':>6s} {'raw bytes':>10s} "
          f"{'hd/raw':>7s} {'tips':>5s}")
    tot_hd = tot_ind = tot_raw = tips = 0
    for app in apps:
        launch(APPS[app]["pkg"])
        first = hd("see")
        second = hd("see", "--no-diff")     # a second look at the same screen, same size
        tree = "\n".join(ln for ln in second.splitlines() if not ln.startswith("#"))
        raw = raw_look(str(wrapper))
        ind = indent_bytes(tree)
        tips += sum(t.count("# TIP") for t in (first, second))
        tot_hd += len(tree)
        tot_ind += ind
        tot_raw += len(raw)
        print(f"{app:10s} {len(tree):9d} {ind:7d} {ind / max(len(tree), 1):5.0%} "
              f"{len(raw):10d} {len(tree) / max(len(raw), 1):6.2f}x "
              f"{sum(t.count('# TIP') for t in (first, second)):5d}")
    print(f"{'TOTAL':10s} {tot_hd:9d} {tot_ind:7d} {tot_ind / max(tot_hd, 1):5.0%} "
          f"{tot_raw:10d} {tot_hd / max(tot_raw, 1):6.2f}x {tips:5d}")
    print("\n`tips` counts the views TIP over two looks at the same screen: >1 per app means it "
          "is being reprinted, which is what the once-per-session guard removes.")
    return check_relative_nesting()


if __name__ == "__main__":
    sys.exit(0 if main(sys.argv[1:] or list(DEFAULT)) else 1)
