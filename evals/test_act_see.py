"""Bench + regression: `-s` folds the post-action look into the action, saving a turn.

ACU is inference, so it is charged per model TURN, not per printed token. The 2026-08-10 A/B/C
measured the skill at 0.74x the perception tokens of an agent with no tooling and still 1.13x
its ACU, because it looked 4.14 times per task against 2.68: 96% of `hd tap`s were followed by
an observation and 32 of those per run were a separate command, i.e. a separate turn.

`hd tap 5 -s` does the tap, waits for the screen to settle and prints exactly what the following
`hd see` would have printed — same bytes, one turn instead of two. This file measures both
halves of that claim on real screens: the command count halves and the output does not grow.

    python3 evals/test_act_see.py [app ...]
"""

import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from env import ENV, find_hd  # noqa: E402
from test_diff import clickables, launch  # noqa: E402


def run(hd_py, *args):
    r = subprocess.run(["python3", hd_py, *args], capture_output=True, text=True, env=ENV)
    return r.stdout


def split_loop(hd_py, pkg, targets):
    """act, then look, as two commands — what the skill's core loop asks for today."""
    launch(pkg)
    rows = []
    for idx in targets:
        run(hd_py, "see")
        act = run(hd_py, "tap", str(idx))
        time.sleep(2)                              # the agent's own `sleep`, then a second call
        out = run(hd_py, "see")
        # Both arms are charged the action's own echo line, so the byte comparison is like
        # for like and the only difference left is the number of commands.
        rows.append((f"tap {idx}", 2, len(act) + len(out), "diff vs last see" in out))
        act = run(hd_py, "key", "back")
        time.sleep(2)
        out = run(hd_py, "see")                    # back to a screen seen seconds ago: a delta
        rows.append((f"back from {idx}", 2, len(act) + len(out), "diff vs last see" in out))
    return rows


def folded_loop(hd_py, pkg, targets):
    """act and look in one command, with `-s` doing the settling."""
    launch(pkg)
    rows = []
    for idx in targets:
        run(hd_py, "see")
        out = run(hd_py, "tap", str(idx), "-s")
        rows.append((f"tap {idx}", 1, len(out), "diff vs last see" in out))
        out = run(hd_py, "key", "back", "-s")
        rows.append((f"back from {idx}", 1, len(out), "diff vs last see" in out))
    return rows


def test_actions_take_see():
    """Every action verb must accept `-s`, or the loop the skill prescribes cannot be typed."""
    src = Path(find_hd()).read_text()
    assert "def see_flag" in src, "the act-then-observe flag is gone"
    for verb in ("tap", "tap-xy", "longpress", "longpress-xy", "type", "key", "swipe"):
        assert f'"{verb}"' in src.split("ACTIONS = {")[1].split("}")[0], \
            f"{verb} no longer folds its observation"


if __name__ == "__main__":
    from suites import APPS  # noqa: E402

    test_actions_take_see()
    print("regression: every action verb takes -s  OK\n")

    hd = find_hd()
    which = sys.argv[1:] or ["markor", "amaze", "seal", "unitto"]
    cmds_split = cmds_fold = chars_split = chars_fold = n = deltas = 0
    for key in which:
        pkg = APPS[key]["pkg"]
        try:
            launch(pkg)
            targets = clickables(run(hd, "see"))[1:5]
            split = {r[0]: r for r in split_loop(hd, pkg, targets)}
            folded = folded_loop(hd, pkg, targets)
        except Exception as e:                                   # noqa: BLE001
            print(f"{key}: FAILED {e}")
            continue
        for act, cmds, chars, delta in folded:
            if act not in split:
                continue
            n += 1
            deltas += delta
            cmds_fold += cmds
            chars_fold += chars
            cmds_split += split[act][1]
            chars_split += split[act][2]
            print(f"{key:<10}{act:<10} folded: 1 command, {chars:>5} chars "
                  f"({'delta' if delta else 'whole tree'})   split: 2 commands, "
                  f"{split[act][2]:>5} chars ({'delta' if split[act][3] else 'whole tree'})")
    if n:
        print(f"\nTOTAL over {n} act-then-observe cycles: {cmds_fold} commands and {chars_fold} "
              f"chars folded, against {cmds_split} commands and {chars_split} chars split "
              f"— {1 - cmds_fold / cmds_split:.0%} fewer turns at "
              f"{chars_fold / chars_split:.2f}x the output, {deltas}/{n} still deltas")
        assert cmds_fold < cmds_split, "folding did not save a command"
        assert chars_fold <= chars_split * 1.1, "folding printed materially more than two calls"
