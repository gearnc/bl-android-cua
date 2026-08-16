"""Bench + regression: an unchained run must be told, while it is paying for the chain it skipped.

The 2026-08-16 A/B/C at `62de67e` (`evals/run-2026-08-16-abc-62de67e/`) left the hybrid/raw
difference in the COUNT of looks, not their price: hybrid paid 429 perception tokens a look
against the raw arm's 329, but took 4.24 looks per task against raw's 2.71, because it chained
1.19 actions per look and raw chained 2.11. `-n` and `hd run` already existed, SKILL.md
led with both, and `hint_no_see` already named `-n` once a session. That is the shape a
once-a-session line has when it is not enough, so the reminder now fires on the behaviour: three
single-action commands in a row, each printing a tree.

What this measures, per app, on the screen the app opens on:

  * fires — three consecutive observing actions print the batch line, and the third one does,
    not the first (two in a row is not yet a batch worth naming);
  * quiet where the caller already batches — actions carrying `-n`, and `hd run`, never
    accumulate a streak, so an agent doing the right thing sees nothing;
  * capped — a session gets STREAK_HINTS lines, not one per action;
  * priced — the line is printed against the size of one auto-look on the same screen, which is
    what a chain of three actions removes two of.

    python3 evals/test_batch_hint.py [app ...]

`$HD_PY` selects the revision under test.
"""
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from env import ADB, ENV, find_hd  # noqa: E402
from test_diff import launch  # noqa: E402

HD = ["python3", find_hd()]
HINT = "single-action commands in a row"
MARKERS = ("/tmp/hd_action_streak", "/tmp/hd_hinted_no_see", "/tmp/hd_looked_only",
           "/tmp/hd_hinted_tap_label")


def hd(*args):
    r = subprocess.run(HD + list(args), capture_output=True, text=True, env=ENV)
    return r.stdout + r.stderr


def fresh_session():
    for m in MARKERS:
        Path(m).unlink(missing_ok=True)


def restart(pkg, deadline=40):
    """Restart `pkg` and wait for it to actually resume.

    A fixed sleep after `monkey` measured the launcher on a cold emulator, which reports the same
    tiny tree for every app and turns the price of a look into a constant.
    """
    subprocess.run([ADB, "shell", "am", "force-stop", pkg], capture_output=True, env=ENV)
    time.sleep(1)
    launch(pkg)
    end = time.time() + deadline
    while time.time() < end:
        r = subprocess.run(["bash", "-c",
                            f"{ADB} shell dumpsys activity activities | grep -m1 ResumedActivity"],
                           capture_output=True, text=True, env=ENV)
        if pkg in r.stdout:
            time.sleep(2)
            return
        time.sleep(2)
    raise AssertionError(f"{pkg} never resumed — the emulator is measuring its launcher")


def noop_action():
    """An action that observes but cannot change the screen, so the trial stays on one screen."""
    return hd("key", "273")            # KEYCODE_NUMPAD_9's neighbour: unhandled by every app here


def test_fires_on_the_third_action(pkg):
    restart(pkg)
    fresh_session()
    hd("see", "-q")
    outs = [noop_action() for _ in range(3)]
    assert HINT not in outs[0] and HINT not in outs[1], \
        f"named the batch forms before there was a batch to name:\n{outs[0][:300]}"
    assert HINT in outs[2], f"three single-action commands, no batch line:\n{outs[2][:400]}"
    return outs[2]


def test_quiet_when_the_caller_batches(pkg):
    restart(pkg)
    fresh_session()
    hd("see", "-q")
    for _ in range(5):
        out = hd("key", "273", "-n")
        assert HINT not in out, f"nagged a caller that was already batching with -n:\n{out[:300]}"
    out = hd("run", "key 273; key 273; key 273", "-n")
    assert HINT not in out, f"nagged a caller that was already using hd run:\n{out[:300]}"
    # And the streak that `hd run` reset does not carry over into the next two actions.
    assert HINT not in noop_action() and HINT not in noop_action(), \
        "the streak survived a batch — the counter is not reset by hd run"


def test_capped_per_session(pkg):
    restart(pkg)
    fresh_session()
    hd("see", "-q")
    fired = sum(HINT in noop_action() for _ in range(40))
    src = Path(find_hd()).read_text()
    cap = int(src.split("STREAK_HINTS = ")[1].split()[0])
    assert fired == cap, f"batch line printed {fired} times in a session, cap is {cap}"
    return cap


def test_source_is_guarded():
    src = Path(find_hd()).read_text()
    assert "def hint_batch" in src, "nothing nudges an unchained run"
    assert "STREAK_HINTS" in src, "the batch line is not capped per session"


def look_bytes(pkg):
    """One look at a screen the caller has not already seen.

    An action that changes nothing folds into a `no change` delta, which is not what chaining
    skips: the actions worth chaining move between screens, so the look each of them buys is a
    tree.
    """
    restart(pkg)
    fresh_session()
    return len(hd("see", "--full", "--no-diff"))


if __name__ == "__main__":
    from suites import APPS  # noqa: E402

    which = sys.argv[1:] or ["markor", "amaze", "seal", "unitto", "joplin", "lesspass"]
    test_source_is_guarded()
    cap = test_capped_per_session(APPS[which[0]]["pkg"])
    print(f"regression: hint exists, capped at {cap} a session  OK\n")

    looks = hints = 0
    for app in which:
        pkg = APPS[app]["pkg"]
        try:
            line = test_fires_on_the_third_action(pkg)
            test_quiet_when_the_caller_batches(pkg)
        except AssertionError as e:
            print(f"{app:<10}FAILED {e}")
            raise
        hint = next(ln for ln in line.splitlines() if HINT in ln)
        look = look_bytes(pkg)
        looks += look
        hints += len(hint)
        print(f"{app:<10}fires on action 3, quiet under -n / hd run  "
              f"(hint {len(hint)}b vs one tree {look}b)")
    print(f"\nTOTAL one line ~{hints // len(which)}b against the {looks // len(which)}b look it "
          f"asks the caller to stop buying ({hints / looks:.1%} of one look), at most {cap} a "
          f"session")
