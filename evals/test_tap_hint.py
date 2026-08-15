"""Bench + regression: the look-bought-an-index idiom must name its own replacement.

`hd tap "PAT"` shipped in #17 and SKILL.md leads with it, so the 2026-08-15 A/B/C at `b3898c3`
was the first matrix where the cheaper form existed. It was typed on 126 of 781 taps (16%), and
100 of the hybrid arm's 252 look-only commands — in 11 of its 12 runs — were still a look followed
by nothing but `hd tap <index>`. Documentation moved that idiom from 115/236 to 100/252 and no
further, the same shape `-s` had at 20% adoption before the fold became the default.

So the hint is printed by the tool, at the instant the caller pays for the thing it replaces:
after an index tap that a standalone look — and no action — preceded. What this bench measures,
per app, on the screen the app opens on:

  * fires — the look → `hd tap <index>` sequence prints the pattern form, naming a real label;
  * truthful — the pattern it suggests taps the SAME node the index just tapped, or the hint is
    worse than silence;
  * once — a session gets one line, not one per tap (`hint_no_see`'s rule);
  * quiet where the idiom is absent — an index tap after an ACTION (whose fold already looked)
    prints nothing, and neither does one whose label matches several distinct nodes.

Cost is one line against the look it is trying to remove: both are printed here.

    python3 evals/test_tap_hint.py [app ...]

`$HD_PY` selects the revision under test.
"""
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from env import ADB, ENV, find_hd  # noqa: E402
from test_diff import launch  # noqa: E402

HD = ["python3", find_hd()]
HINT = re.compile(r'`hd tap "((?:[^"\\]|\\.)+)"`')
TAPPED = re.compile(r"at \((\d+),(\d+)\)")
ROW = re.compile(r'^\s*\[(\d+)\](?=.*<C)')
MARKERS = ("/tmp/hd_hinted_tap_label", "/tmp/hd_looked_only")


def hd(*args):
    r = subprocess.run(HD + list(args), capture_output=True, text=True, env=ENV)
    return r.stdout + r.stderr, r.returncode


def fresh_session():
    """A hint is once per SESSION, so every trial starts from an unhinted one."""
    for m in MARKERS:
        Path(m).unlink(missing_ok=True)


def where(out):
    m = TAPPED.search(out)
    return (int(m.group(1)), int(m.group(2))) if m else None


def clickables(tree):
    return [int(m.group(1)) for ln in tree.splitlines() if (m := ROW.match(ln))]


def restart(pkg):
    subprocess.run([ADB, "shell", "am", "force-stop", pkg], capture_output=True, env=ENV)
    time.sleep(1)
    launch(pkg)


def trial(app, pkg):
    """The run's idiom, once per clickable node until one of them is nameable."""
    restart(pkg)
    tree, _ = hd("see", "--full", "--no-diff")
    for idx in clickables(tree)[:12]:
        fresh_session()
        look, _ = hd("see", "--find", ".")
        act, _ = hd("tap", str(idx), "-n")
        m = HINT.search(act)
        if not m:
            continue                       # unlabeled or ambiguous row: silence is correct
        at = where(act)
        # The suggestion has to be executable as printed, against the same screen.
        restart(pkg)
        hd("see", "-q")
        again, rc = hd("tap", m.group(1), "-n")
        return dict(app=app, label=m.group(1), same=rc == 0 and where(again) == at,
                    look_bytes=len(look), hint_bytes=len(m.group(0)) + 60, idx=idx)
    return dict(app=app, label=None, same=False, look_bytes=0, hint_bytes=0, idx=None)


def test_hint_is_once_per_session(pkg):
    restart(pkg)
    fresh_session()
    tree, _ = hd("see", "--full", "--no-diff")
    idx = str(clickables(tree)[0])
    first = ""
    for _ in range(4):
        hd("see", "--find", ".")
        out, _ = hd("tap", idx, "-n")
        if HINT.search(out):
            assert not first, f"the hint printed twice in one session:\n{out[:300]}"
            first = out
    assert first, "no hint at all on a look-then-index-tap sequence"


def test_an_action_before_the_tap_is_not_a_look(pkg):
    """The fold already observed inside the previous command — nothing was bought twice."""
    restart(pkg)
    fresh_session()
    tree, _ = hd("see", "--full", "--no-diff")
    idx = str(clickables(tree)[0])
    hd("key", "menu", "-n")
    out, _ = hd("tap", idx, "-n")
    assert not HINT.search(out), f"hinted after an action, where no look was spent:\n{out[:300]}"


def test_hint_source_is_guarded():
    src = Path(find_hd()).read_text()
    assert "def hint_tap_label" in src, "no hint for the look-bought-an-index idiom"
    assert "HINTED_LABEL" in src, "the hint is not capped at once per session"


if __name__ == "__main__":
    from suites import APPS  # noqa: E402

    which = sys.argv[1:] or ["markor", "amaze", "seal", "unitto", "joplin", "lesspass"]
    first_pkg = APPS[which[0]]["pkg"]
    test_hint_source_is_guarded()
    test_hint_is_once_per_session(first_pkg)
    test_an_action_before_the_tap_is_not_a_look(first_pkg)
    print("regression: hint exists, fires once, stays quiet after an action  OK\n")

    fired = truthful = 0
    looks = hints = 0
    for app in which:
        try:
            r = trial(app, APPS[app]["pkg"])
        except Exception as e:                                   # noqa: BLE001
            print(f"{app}: FAILED {e}")
            continue
        if r["label"]:
            fired += 1
            truthful += r["same"]
            looks += r["look_bytes"]
            hints += r["hint_bytes"]
            print(f"{app:<10}[{r['idx']}] -> suggests hd tap {r['label'][:24]!r:<26} "
                  f"same node: {'yes' if r['same'] else 'NO'}  "
                  f"(look {r['look_bytes']}b vs hint ~{r['hint_bytes']}b)")
            assert r["same"], f"{app}: the suggested pattern did not tap the node the index did"
        else:
            print(f"{app:<10}no nameable clickable in the first 12 rows — no hint, correct")
    if fired:
        print(f"\nTOTAL fired on {fired}/{len(which)} apps, {truthful}/{fired} suggested a "
              f"pattern that tapped the same node")
        print(f"  one hint ~{hints // fired}b against the {looks // fired}b look it removes "
              f"({hints / looks:.1%} of it), printed once per session")
