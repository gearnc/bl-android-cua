"""Bench + regression: a delta must be measured against a tree the caller was actually shown.

`hd see --find` renders the whole tree (indexes must stay valid for `hd tap`) but prints only the
matching lines; `hd see -q` prints nothing at all. Recording either as the diff baseline makes the
*next* `hd see` compare the screen against a tree nobody read, so it answers

    # screen 720x1280, +0 -0 of 5 nodes (diff vs last see ...)
    # no change since the last see

about a screen the caller has never seen. It is silent — the caller has no way to tell that
"no change" means "unchanged since a tree that was never printed" — and it is common: in the
2026-08-10 A/B/C, `--find` was 62% of the hybrid arm's 1,016 observation calls and 164 of the 287
plain re-observations (57%) directly followed a `--find`/`-q`/`--full`.

This bench prices information, not brevity: after `see -> act -> see --find -> act -> see`, how
many nodes of the screen now in front of the agent have never been printed to it. A revision that
prints a cheap empty delta scores *worse* here, which is the point — the previous bench
(`test_find_baseline.py`) counts deltas and would call that an improvement.

    python3 evals/test_seen_baseline.py [app ...]

`$HD_PY` selects the revision under test, `$HD_PY_OLD` the one to compare against (default: this
file's committed parent revision via `git show`).
"""

import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from env import ADB, ENV, find_hd  # noqa: E402
from test_diff import clickables, launch  # noqa: E402

STATE = "/tmp/hd_last_tree.json"
NODE = re.compile(r"^\s*[+-]?\s*\[\d+\]\s*(.*)$")


TIMEOUT = 90   # a wedged `uiautomator dump` should cost one row, not the whole bench


def run(hd_py, *args):
    try:
        return subprocess.run(["python3", hd_py, *args], capture_output=True, text=True,
                              env=ENV, timeout=TIMEOUT).stdout
    except subprocess.TimeoutExpired:
        subprocess.run([ADB, "shell", "pkill", "-f", "uiautomator"], capture_output=True, env=ENV)
        return ""


def nodes_in(text):
    """Node identities (index stripped) mentioned in a rendered tree or a `+`/`-` delta."""
    return {m.group(1).strip() for m in (NODE.match(ln) for ln in text.splitlines()) if m}


def truth(hd_py):
    """The compact tree really on screen, without disturbing the state the agent is using."""
    saved = Path(STATE).read_bytes() if os.path.exists(STATE) else None
    try:
        return nodes_in(run(hd_py, "see", "--no-diff"))
    finally:
        if saved is None:
            Path(STATE).unlink(missing_ok=True)
        else:
            Path(STATE).write_bytes(saved)


def loop(hd_py, pkg, targets):
    """observe -> act -> `--find` -> observe, the way agents actually drive.

    The last `see` asks "what am I looking at now?" about a screen the caller has not been shown:
    the tap changed it and `--find` printed only its matches. Returns one row per re-observation:
    (label, chars printed, nodes of the current screen never shown to the caller).
    """
    rows = []
    for idx in targets:
        # Relaunch per row: `key back` on an app's own home screen leaves the app entirely, and
        # the next row would then measure whatever app was behind it.
        launch(pkg)
        # Start each row from a tree the caller demonstrably holds, so "never shown" below is
        # about the interleaving under test and not about where the previous row left off.
        first = run(hd_py, "see", "--no-diff")
        run(hd_py, "tap", str(idx))
        time.sleep(2)
        run(hd_py, "see", "--find", "Button|Text|View|Menu")   # the interleaved verb under test
        out = run(hd_py, "see")                                # "what am I looking at now?"
        seen = nodes_in(first) | nodes_in(out)
        rows.append((f"tap {idx}", len(out), len(truth(hd_py) - seen)))
        run(hd_py, "key", "back")                              # back to the row's start screen
        time.sleep(2)
    return rows


def old_revision():
    """The committed parent of the current hd.py, so the bench prices its own change."""
    if os.environ.get("HD_PY_OLD"):
        return os.environ["HD_PY_OLD"]
    rel = "skills/android-hybrid-navigation/hd.py"
    repo = Path(__file__).resolve().parents[1]
    src = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=repo,
                         capture_output=True, text=True)
    if src.returncode:
        return ""
    out = Path("/tmp/hd_prev.py")
    out.write_text(src.stdout)
    return str(out)


def test_unprinted_render_keeps_the_baseline():
    """`--find`/`-q` must not become the tree the next `see` diffs against."""
    src = Path(find_hd()).read_text()
    assert "if not quiet and not find:" in src, "an unprinted render sets the baseline again"
    assert '"baselines"' in src, "state file no longer keeps per-rendering baselines"


if __name__ == "__main__":
    from suites import APPS  # noqa: E402

    test_unprinted_render_keeps_the_baseline()
    print("regression: an unprinted render leaves the baseline alone  OK\n")

    if not shutil.which("adb") and not Path(ADB).exists():
        sys.exit("adb not found — start the emulator first")
    fixed, old = find_hd(), old_revision()
    which = sys.argv[1:] or ["markor", "amaze", "seal", "unitto"]
    n = blind_new = blind_old = chars_new = chars_old = 0
    for key in which:
        pkg = APPS[key]["pkg"]
        try:
            launch(pkg)
            targets = clickables(run(fixed, "see", "--no-diff"))[1:4]
            rows = loop(fixed, pkg, targets)
            was = {r[0]: r for r in loop(old, pkg, targets)} if old else {}
        except Exception as e:                                   # noqa: BLE001
            print(f"{key}: FAILED {e}")
            continue
        for act, chars, blind in rows:
            n += 1
            blind_new += blind
            chars_new += chars
            blind_old += was[act][2] if act in was else blind
            chars_old += was[act][1] if act in was else chars
            tail = f"  old={was[act][2]:>3} unseen in {was[act][1]:>6} chars" if act in was else ""
            print(f"{key:<10}{act:<10} unseen={blind:>3} nodes in {chars:>6} chars{tail}")
    if n:
        print(f"\nTOTAL over {n} re-observations after a `--find`: "
              f"{blind_new} unseen nodes in {chars_new} chars")
        if old:
            print(f"previous revision: {blind_old} unseen nodes in {chars_old} chars")
            assert blind_new <= blind_old, "the fix left the caller blind to more nodes"
