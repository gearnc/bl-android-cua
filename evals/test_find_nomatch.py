"""Bench + regression: what a `hd see --find` that matches nothing costs.

A `--find` miss used to print two lines — the count, and "re-run without --find (or --full)
before concluding it's absent". That is an instruction to spend another turn, and the agents
obeyed it: over the 12 hybrid runs of the 2026-08-11 A/B/C matrix, 40 plain re-observations
followed a `--find` with no action in between, on top of ~7 `NO MATCH` prints per run. Turns are
what ACU bills (hybrid spent 180 turns against bare's 158 for the same task list), so a verb that
answers "nothing, ask again" is a verb that costs two looks to deliver one.

The fix prints the compact tree on a miss, the way the <5-node case already auto-escalates. This
bench prices both halves of that trade, per app:

    commands   what the caller must run to end up holding the screen (2 -> 1)
    chars      what those commands print into its context

A miss now costs more characters in exchange for a whole turn, so the bench asserts the character
cost stays within what the follow-up `see` would itself have printed — i.e. the fix must not
print the tree twice. The few percent of slack is the escalated tree's own indexes: they address
the full rendering a `--find` matched against, so they run into two digits where a compact
re-render would have counted 0..4 — and a re-render's indexes tap the wrong node.

    python3 evals/test_find_nomatch.py [app ...]

`$HD_PY` selects the revision under test, `$HD_PY_OLD` the one to compare against (default: this
file's committed parent revision via `git show`).
"""
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from env import ADB, ENV, find_hd  # noqa: E402
from plan import DEFAULT_APPS  # noqa: E402
from test_diff import launch  # noqa: E402
from test_seen_baseline import old_revision, run  # noqa: E402

MISS = "ZZQQNOSUCHNODE"


def one_look(hd_py):
    """(commands, chars) for a `--find` miss followed by whatever the caller must do next."""
    out = run(hd_py, "see", "--find", MISS)
    if "NO MATCH" not in out:
        raise AssertionError(f"pattern {MISS!r} matched something — pick a rarer one")
    # The old revision tells the caller to re-run without --find; the new one has already
    # printed the tree, so there is nothing left to run.
    if "re-run without --find" in out:
        return 2, len(out) + len(run(hd_py, "see", "--no-diff"))
    return 1, len(out)


def test_miss_prints_the_tree():
    src = Path(find_hd()).read_text()
    assert "re-run without --find" not in src, "a `--find` miss still asks for another look"
    assert "so this costs one look, not two" in src, "the miss no longer escalates to the tree"
    assert "re-observe before concluding" not in src, "a cached `hd find` miss still asks too"


def node_lines(out):
    return [ln.strip() for ln in out.splitlines() if ln.strip().startswith("[")]


def test_escalated_indexes_are_tappable(hd_py):
    """Every line an escalation prints must be a line of the tree `hd tap` indexes against.

    Both misses match against the FULL rendering, so escalating to a compact RE-render hands the
    caller indexes counted 0..n over a different node set: `hd tap 4` off such a tree tapped a
    FrameLayout at the screen's centre instead of the ImageButton printed beside the 4. A subset
    of the cached lines cannot drift that way, and this is the cheapest way to state it.
    """
    # `--no-diff`: the reference has to be the whole tree `hd tap` indexes against, and a
    # re-observation of a screen already shown prints only its delta.
    cached = node_lines(run(hd_py, "see", "--full", "--no-diff"))
    for verb in (("see", "--find", MISS), ("find", MISS)):
        printed = node_lines(run(hd_py, *verb))
        assert printed, f"`hd {' '.join(verb)}` printed no tree on a miss"
        stray = [ln for ln in printed if ln not in cached]
        assert not stray, (f"`hd {' '.join(verb)}` printed indexes that address nothing "
                           f"`hd tap` knows about: {stray[:2]}")


if __name__ == "__main__":
    test_miss_prints_the_tree()
    print("regression: a `--find` miss prints the tree instead of asking for it  OK")

    if not shutil.which("adb") and not Path(ADB).exists():
        sys.exit("adb not found — start the emulator first")
    subprocess.run([ADB, "root"], capture_output=True, env=ENV)
    fixed, old = find_hd(), old_revision()
    which = sys.argv[1:] or list(DEFAULT_APPS)
    from suites import APPS  # noqa: E402
    launch(APPS[which[0]]["pkg"])
    test_escalated_indexes_are_tappable(fixed)
    print("regression: an escalated tree's indexes address the cached tree  OK\n")
    print(f"{'app':<12}{'cmds':>6}{'chars':>8}   {'old cmds':>9}{'old chars':>10}")
    tot = [0, 0, 0, 0]
    for key in which:
        try:
            launch(APPS[key]["pkg"])
            c_new, n_new = one_look(fixed)
            launch(APPS[key]["pkg"])
            c_old, n_old = one_look(old) if old else (c_new, n_new)
        except Exception as e:                                   # noqa: BLE001
            print(f"{key:<12}FAILED {e}")
            continue
        tot = [a + b for a, b in zip(tot, (c_new, n_new, c_old, n_old))]
        print(f"{key:<12}{c_new:>6}{n_new:>8}   {c_old:>9}{n_old:>10}")
    if tot[0]:
        print(f"\nTOTAL over {len(which)} apps: {tot[0]} commands / {tot[1]:,} chars, "
              f"previously {tot[2]} commands / {tot[3]:,} chars")
        assert tot[0] <= tot[2], "the fix costs more commands than it saves"
        assert tot[1] <= tot[3] * 1.15, "the fix printed the tree twice"
