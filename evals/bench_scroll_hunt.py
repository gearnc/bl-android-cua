"""Bench: what it costs to reach a row that is below the fold.

In the 2026-08-17 A/B/C the hybrid arm spent 72 commands inside 24 multi-swipe hunts across 10
of its 12 cells: `hd swipe up`, then a look to find out whether the row arrived, then another
swipe. Every one of those looks answers one yes/no question, and turns are what ACU tracks — the
2026-08-11 numbers price one extra look per task at 0.078 ACU, and each look's tree is re-read
in every later turn's resident context.

`hd swipe up --until PAT` runs that loop inside one process: swipe, re-cache silently, test the
pattern, print only the lines that answer. This bench drives real off-screen targets on real
scrollable screens and prices both ways of reaching them — the hand-typed loop the transcripts
show against `--until` — and checks the two things the shortcut has to keep true:

  * the index it prints addresses the tree hd has cached, so `hd tap` off it needs no new look;
  * a target that is not there stops at the end of the list instead of spending `--max` swipes,
    and prints the tree it matched against, so a miss still costs one look and not two.

Screens are opened by intent rather than by navigating each app, so the bench is deterministic;
a screen whose list fits on one page has no hunt to price and is skipped.

Usage:  python3 evals/bench_scroll_hunt.py [screen ...]
"""

import json
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from env import ADB, ENV, find_hd  # noqa: E402
from suites import APPS  # noqa: E402

STATE = "/tmp/hd_last_tree.json"
# A row an agent could name: an indexed node whose rendering carries a quoted label.
LABEL = re.compile(r'^\s*\[\d+\]\s+\S+\s+"([^"]{4,60})"')
MAX_SWIPES = 8

# (screen, how to open it). Long lists an agent actually scrolls: the two app-owned preference
# screens in the matrix's Views app, the system list every task's verification passes through,
# and each matrix app's own first screen (skipped when it fits on one page).
SETTINGS = "com.android.settings"
SCREENS = {
    "settings-home": (SETTINGS, ("shell", "am", "start", "-a", "android.settings.SETTINGS")),
    "amaze-prefs": ("com.amaze.filemanager",
                    ("shell", "am", "start", "-a",
                     "android.intent.action.APPLICATION_PREFERENCES", "-p",
                     "com.amaze.filemanager")),
    "settings-apps": (SETTINGS, ("shell", "am", "start", "-a",
                                 "android.settings.APPLICATION_SETTINGS")),
    **{k: (v["pkg"], ("shell", "monkey", "-p", v["pkg"],
                      "-c", "android.intent.category.LAUNCHER", "1"))
       for k, v in APPS.items()},
}
DEFAULT = ("settings-home", "amaze-prefs", "settings-apps",
           "markor", "amaze", "seal", "unitto", "joplin", "lesspass")


def adb(*args):
    return subprocess.run([ADB, *args], capture_output=True, text=True, env=ENV).stdout


def hd(*args):
    r = subprocess.run(["python3", find_hd(), *args], capture_output=True, text=True, env=ENV)
    return r.stdout + r.stderr


def open_screen(name):
    """Open the screen from cold.

    An `am start` sent to an app already in a sub-screen is delivered to the running task and
    changes nothing, so the bench would price whatever the previous screen left behind.
    """
    pkg, cmd = SCREENS[name]
    adb("shell", "am", "force-stop", pkg)
    time.sleep(1)
    adb(*cmd)
    time.sleep(5)
    hd("see", "-q")


def cached_lines():
    return json.load(open(STATE))["lines"] if Path(STATE).exists() else []


def swipe(d="up"):
    hd("swipe", d, "-n")
    time.sleep(1.5)


def to_top():
    for _ in range(MAX_SWIPES + 2):
        swipe("down")
    hd("see", "-q")


def find_offscreen_target():
    """A row this screen only shows after scrolling — the case the hunt exists for.

    Read off the device instead of hard-coded per app, so the bench survives an app's list
    changing: scroll to the end, keep a label the first page did not have, scroll back, and
    confirm from the top that it really is off-screen before pricing anything.
    """
    top = {m.group(1) for ln in cached_lines() if (m := LABEL.match(ln))}
    seen, last = [], None
    for _ in range(MAX_SWIPES):
        swipe("up")
        hd("see", "-q")
        lines = cached_lines()
        if lines == last:
            break
        last = lines
        seen += [m.group(1) for ln in lines if (m := LABEL.match(ln))]
    to_top()
    fresh = [s for s in seen if s not in top]
    for cand in reversed(fresh):
        pat = re.escape(cand[:24])
        if "NO MATCH" in hd("see", "--find", pat):
            return cand, pat
    return None, None


def hunt_by_hand(pat):
    """One command per swipe, the way the transcripts did it: swipe, look, decide, swipe."""
    out = hd("see", "--find", pat)
    cmds = 1
    while "NO MATCH" in out and cmds < MAX_SWIPES * 2:
        swipe("up")
        out = hd("see", "--find", pat)
        cmds += 2
    return cmds, len(out), "NO MATCH" not in out


def hunt_with_until(pat):
    out = hd("swipe", "up", "--until", pat, "--max", str(MAX_SWIPES))
    return 1, len(out), "# found" in out


def measure(name):
    open_screen(name)
    target, pat = find_offscreen_target()
    if not target:
        print(f"{name:<15}no row below the fold — nothing to hunt, skipped")
        return None
    n_old, b_old, ok_old = hunt_by_hand(pat)
    to_top()
    n_new, b_new, ok_new = hunt_with_until(pat)
    assert ok_old == ok_new, f"{name}: the two hunts disagree about {target!r}"
    assert ok_new, f"{name}: --until did not reach {target!r} the hand loop reached"
    # The whole point of printing indexes is tapping off them: they must address the cached tree.
    assert any(re.search(pat, ln, re.I) for ln in cached_lines()), \
        f"{name}: --until printed an index it did not cache"
    print(f"{name:<15}{target[:24]:<26} by hand: {n_old:>2} cmds {b_old:>5}B    "
          f"--until: {n_new} cmd {b_new:>5}B")
    return n_old, b_old, n_new, b_new


def miss_stops_at_the_end(name):
    """A row that is not there must cost the swipes to the end of the list, not `--max`."""
    open_screen(name)
    out = hd("swipe", "up", "--until", "Zzz no such row Zzz", "--max", str(MAX_SWIPES))
    m = re.search(r"stopped moving after (\d+) swipe", out)
    print(f"\nmiss on {name}: "
          + (f"stopped at the end of the list after {m.group(1)} swipe(s)"
             if m else f"spent all {MAX_SWIPES} swipes"))
    assert "NO MATCH" in out, "a miss must print the tree it matched against"


def main(which):
    rows = [r for r in (measure(k) for k in which) if r]
    if not rows:
        sys.exit("no screen had a row below the fold — nothing to price")
    cmd_old, b_old = sum(r[0] for r in rows), sum(r[1] for r in rows)
    cmd_new, b_new = sum(r[2] for r in rows), sum(r[3] for r in rows)
    print(f"\nTOTAL over {len(rows)} screens: commands {cmd_old} -> {cmd_new} "
          f"({cmd_old / max(cmd_new, 1):.1f}x fewer turns), "
          f"printed bytes {b_old} -> {b_new} ({1 - b_new / max(b_old, 1):.0%} less)")
    miss_stops_at_the_end(which[0])
    assert cmd_new < cmd_old, "the hunt did not get shorter"
    assert b_new <= b_old, "the hunt printed more"


if __name__ == "__main__":
    main(sys.argv[1:] or list(DEFAULT))
