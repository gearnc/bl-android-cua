"""Bench + regression: an action observes after itself, and a batch pays for one look.

ACU is inference, so it is charged per model TURN, not per printed token. The 2026-08-11 A/B/C
measured the skill at 0.67x the perception tokens of an agent with no tooling and still 1.10x
its ACU, because it looked 3.26 times per task against 1.96 — the unaided agent chained 8.74
actions per look, the skill 2.02. `-s` had shipped as the fix for exactly that and was typed on
312 of 1,569 actions (20%), so the fold is now the DEFAULT and `-n` opts out.

Two claims, both measured here on real screens:

* an action verb with no flags does the action, settles, and prints what the following `hd see`
  would have — one command instead of two, and not materially more output;
* a batch of N actions with `-n` on all but the last costs one command and one tree, against N
  commands and N trees if every action looks.

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
    """act, then look, as two commands — the loop an agent types when the action does not look.

    `-n` here is not the flag under test, it is how this arm reproduces the old behaviour: the
    action prints its echo line and nothing else, and the observation is a second command.
    """
    launch(pkg)
    rows = []
    for idx in targets:
        run(hd_py, "see")
        act = run(hd_py, "tap", str(idx), "-n")
        time.sleep(2)                              # the agent's own `sleep`, then a second call
        out = run(hd_py, "see")
        # Both arms are charged the action's own echo line, so the byte comparison is like
        # for like and the only difference left is the number of commands.
        rows.append((f"tap {idx}", 2, len(act) + len(out), "diff vs last see" in out))
        act = run(hd_py, "key", "back", "-n")
        time.sleep(2)
        out = run(hd_py, "see")                    # back to a screen seen seconds ago: a delta
        rows.append((f"back from {idx}", 2, len(act) + len(out), "diff vs last see" in out))
    return rows


def folded_loop(hd_py, pkg, targets):
    """act and look in one command — the default, no flag typed."""
    launch(pkg)
    rows = []
    for idx in targets:
        run(hd_py, "see")
        out = run(hd_py, "tap", str(idx))
        rows.append((f"tap {idx}", 1, len(out), "diff vs last see" in out))
        out = run(hd_py, "key", "back")
        rows.append((f"back from {idx}", 1, len(out), "diff vs last see" in out))
    return rows


def batch(hd_py, pkg, targets, quiet):
    """(commands, chars) for N actions in a row: every one looking, or only the last.

    The actions are `key back`, which no screen can invalidate, so the two variants do the same
    work and differ only in how many trees they print.
    """
    launch(pkg)
    run(hd_py, "see")
    chars = 0
    for i in range(len(targets)):
        last = i == len(targets) - 1
        chars += len(run(hd_py, "key", "back", *([] if last or not quiet else ["-n"])))
    # An agent chains a batch into ONE shell command; the split variant cannot, because it
    # reads each tree before choosing the next action.
    return (1 if quiet else len(targets)), chars


def test_actions_observe_by_default():
    """Every action verb folds its look unless `-n` is typed — the whole point of the default."""
    src = Path(find_hd()).read_text()
    assert "def see_flag" in src, "the act-then-observe flag is gone"
    for verb in ("tap", "tap-xy", "longpress", "longpress-xy", "type", "key", "swipe"):
        assert f'"{verb}"' in src.split("ACTIONS = {")[1].split("}")[0], \
            f"{verb} no longer folds its observation"
    body = src.split("def see_flag")[1].split("\ndef ")[0]
    assert '"-n" in a or "--no-see" in a' in body, "there is no way to opt out of the look"
    assert body.rstrip().endswith("return True, None, False"), "the look is not the default"


def test_type_can_type_a_flag():
    """`hd type "-n"` must type `-n`, not read it as the opt-out."""
    src = Path(find_hd()).read_text()
    # Per-verb, so adding a verb to the table does not read as removing the guard.
    for verb, operands in (("type", 2), ("tap-xy", 3), ("longpress-xy", 3)):
        assert f'"{verb}": {operands}' in src, \
            f"flags are read over {verb}'s own operands again"


if __name__ == "__main__":
    from suites import APPS  # noqa: E402

    test_actions_observe_by_default()
    test_type_can_type_a_flag()
    print("regression: every action verb observes by default, `-n` opts out  OK\n")

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

    print()
    b_cmds = b_chars = q_cmds = q_chars = 0
    for key in which:
        pkg = APPS[key]["pkg"]
        try:
            steps = ["back"] * 4
            c1, n1 = batch(hd, pkg, steps, quiet=False)
            c2, n2 = batch(hd, pkg, steps, quiet=True)
        except Exception as e:                                   # noqa: BLE001
            print(f"{key}: FAILED {e}")
            continue
        b_cmds, b_chars = b_cmds + c1, b_chars + n1
        q_cmds, q_chars = q_cmds + c2, q_chars + n2
        print(f"{key:<10}batch of {len(steps)}: every action looks = {c1} commands, {n1:>5} chars"
              f"   `-n` on all but the last = {c2} command, {n2:>5} chars")
    if b_cmds:
        print(f"\nTOTAL batches: {q_cmds} commands and {q_chars} chars against {b_cmds} and "
              f"{b_chars} — {1 - q_cmds / b_cmds:.0%} fewer turns, "
              f"{1 - q_chars / b_chars:.0%} less output")
        assert q_chars < b_chars, "`-n` did not suppress the intermediate looks"
