"""Bench + regression: replacing a field's contents must not be a guessed backspace loop.

`hd type` appends. Editing a value that is already in the field — a filename, a URL, a
template, a subtitle-language list — therefore fell outside the skill, and the agent left it:
in the 2026-08-12 A/B/C the hybrid arm hand-rolled 28 deletion loops across 8 of its 12 runs,
405 `keyevent 67`s, and re-guessed the count on the same field (seal|hybrid|1 sent 20, then 30,
then 10, 30, 30, 40, 20, 40, 20). Every guess is a turn, and a wrong one costs a second: too few
leaves a prefix of the old value fused to the new text, too many eats into whatever the field
had before it.

hd never had to guess — it dumps the tree anyway, and the tree carries the focused field's
text. `hd type "x" -r` deletes exactly `len(text)` characters in a single `input keyevent` call
and types.

This bench prices the guess, not the flag: for each field it runs the two idioms an agent
actually has and checks what ends up IN the field.

    python3 evals/test_replace.py [app ...]

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

TIMEOUT = 90
FIELD = re.compile(r"^\s*\[(\d+)\]\s+EditText\s+(\"(?:[^\"\\]|\\.)*\")?")
# What an agent types when it has to guess: it has no character count, so it picks a round
# number and hopes. These are the two failure directions, both observed in the run.
GUESSES = (10, 40)


def run(*args, hd_py=None):
    try:
        return subprocess.run(["python3", hd_py or find_hd(), *args], capture_output=True,
                              text=True, env=ENV, timeout=TIMEOUT).stdout
    except subprocess.TimeoutExpired:
        subprocess.run([ADB, "shell", "pkill", "-f", "uiautomator"], capture_output=True, env=ENV)
        return ""


def fields(tree):
    """(index, current text) for every EditText in a rendered tree."""
    out = []
    for line in tree.splitlines():
        m = FIELD.match(line)
        if m:
            out.append((int(m.group(1)), (m.group(2) or '""')[1:-1]))
    return out


def current_field(k):
    """Index of the k-th field on the screen as it is right now (IME open, tree renumbered)."""
    found = fields(run("see", "--full", "--no-diff"))
    return found[k][0] if k < len(found) else None


def value_of(k):
    """What the k-th field holds now, read back off a fresh tree.

    Addressed by position, never by index: opening the IME inserts nodes and renumbers the tree,
    so the index that named the field before typing names something else after it.
    """
    found = fields(run("see", "--full", "--no-diff"))
    return found[k][1] if k < len(found) else None


def nth_field(pkg, k):
    """Index of the k-th EditText on the app's start screen, re-resolved from a fresh tree.

    Indexes shift the moment the IME opens, so every trial re-launches and re-reads rather than
    reusing an index found before the previous trial typed anything.
    """
    launch(pkg)
    found = fields(run("see", "--full", "--no-diff"))
    return found[k][0] if k < len(found) else None


def seed_field(pkg, k, seed):
    """Put a known value in the k-th field. False when it refuses one (numeric, masked)."""
    idx = nth_field(pkg, k)
    if idx is None:
        return False
    run("tap", str(idx), "-n")
    run("type", seed, "-r", "-n")
    time.sleep(1)
    return value_of(k) == seed


def manual_replace(index, new, dels):
    """The idiom the run is full of: MOVE_END, a guessed number of DELs, then type."""
    run("tap", str(index), "-n")
    subprocess.run([ADB, "shell", "input", "keyevent", "123", *(["67"] * dels)],
                   capture_output=True, env=ENV)
    run("type", new, "-n")
    time.sleep(1)


def hd_replace(index, new):
    run("tap", str(index), "-n")
    run("type", new, "-r", "-n")
    time.sleep(1)


def test_replace_deletes_exactly_what_the_field_holds():
    src = Path(find_hd()).read_text()
    assert "def clear_focused" in src, "no field-clearing primitive"
    assert "len(old)" in src, "the deletion count is not taken from the field's own text"
    assert '"focused"' in src, "the tree does not record which field is focused"


if __name__ == "__main__":
    from suites import APPS  # noqa: E402

    test_replace_deletes_exactly_what_the_field_holds()
    print("regression: the deletion count comes from the tree  OK\n")

    which = sys.argv[1:] or ["lesspass"]
    seed, new = "seedvalue-0123456789", "replaced"
    n = ok_hd = 0
    ok_guess = {g: 0 for g in GUESSES}
    for key in which:
        pkg = APPS[key]["pkg"]
        try:
            for k in range(3):
                if nth_field(pkg, k) is None:
                    break
                # Both idioms must face the same non-empty value.
                if not seed_field(pkg, k, seed):
                    print(f"{key:<10}field #{k} skipped (holds no plain text)")
                    continue
                n += 1
                hd_replace(current_field(k), new)
                got_hd = value_of(k)
                ok_hd += got_hd == new
                got = {}
                for g in GUESSES:
                    seed_field(pkg, k, seed)
                    manual_replace(current_field(k), new, g)
                    got[g] = value_of(k)
                    ok_guess[g] += got[g] == new
                print(f"{key:<10}field #{k} -r -> {got_hd!r:<24}"
                      + "".join(f"  seq {g} -> {got[g]!r}" for g in GUESSES))
        except Exception as e:                                   # noqa: BLE001
            print(f"{key}: FAILED {e}")
    if n:
        print(f"\nTOTAL {n} fields, one command each:")
        print(f"  hd type -r        {ok_hd}/{n} replaced exactly")
        for g in GUESSES:
            print(f"  guessed {g:<3} DELs  {ok_guess[g]}/{n} replaced exactly")
        assert ok_hd == n, "`-r` did not replace every field exactly"
