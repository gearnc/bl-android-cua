#!/usr/bin/env python3
"""Bench `hd run` (one command, one look) against the same flow typed step by step.

The measurement that motivates the verb: across the ten archived A/B/C runs the hybrid arm's
ACU sits at ~1.08x bare while its perception tokens sit at ~0.8x, because ACU follows TURNS
(billed input is resident context integrated over turns, `billed.py`) and hybrid types roughly
one action per command — ~3.3 looks per task against bare's ~2.2. Every per-look byte saver
stalled at 15-20% adoption without moving the ACU ratio. `hd run` compresses the turns
themselves: N actions, one process, one printed tree.

Protocol, per app: launch, one setup `hd see`, then the SAME flow both ways —
  singles: each step typed as its own `hd` command, each folding its default observation
           (exactly what an agent that never batches pays);
  batch:   one `hd run 'step; step; …' --find VERIFY`.
Every flow is reversible (ends on the screen it started from), so the two variants start from
identical state. Both variants must end with the VERIFY pattern on screen; a variant that
cannot prove its end state is a failure, not a data point.

Also regression-checks the batch contract: pre-validation rejects an unknown verb and a
non-first index tap without touching the device, and a failing step stops the batch, names it,
and exits nonzero.
"""
import re
import shlex
import subprocess
import sys
import time

HD = ["python3", "skills/android-hybrid-navigation/hd.py"]

# Steps are hd verbs exactly as `hd run` takes them; each flow is reversible.
APPS = {
    "markor": ("net.gsantner.markor",
               ['tap "To-Do"', 'tap "QuickNote"', 'tap "Files"'],
               r"Create a new file"),
    "amaze": ("com.amaze.filemanager",
              ['tap "Alarms"', "key back", "wait-idle"],
              r"folders and"),
    "seal": ("com.junkfood.seal",
             ['tap "Downloads"', "key back", 'tap "Settings"', "key back"],
             r"Video link"),
    # Unitto's digit keys are anonymous Views that adopt neighbouring labels (three keys render
    # `near:"Clear"`), so the flow sticks to labels that name exactly one key. The verification
    # is the expression the taps typed, which the tree prints JSON-escaped.
    "unitto": ("com.sadellie.unitto",
               ['tap "Pi"', 'tap "Multiply"', 'tap "Pi"'],
               r"\\u03c0\\u00d7\\u03c0"),
    "joplin": ("net.cozic.joplin",
               ['tap "1\\. Welcome"', "key back", "wait-idle"],
               r"All notes"),
    "lesspass": ("com.lesspass.android",
                 ['tap "Settings"', "wait-idle", 'tap ", LessPass"'],
                 r"GENERATE"),
}


def hd(*args):
    r = subprocess.run(HD + list(args), capture_output=True, text=True, timeout=180)
    return r.returncode, r.stdout + r.stderr


def launch(pkg):
    subprocess.run(["adb", "shell", "monkey", "-p", pkg, "-c",
                    "android.intent.category.LAUNCHER", "1"],
                   capture_output=True, timeout=30)
    time.sleep(5)


def contract_checks():
    rc, out = hd("run", 'frobnicate "x"; key back')
    assert rc != 0 and "not a batchable verb" in out, out
    rc, out = hd("run", 'key back; tap 3')
    assert rc != 0 and "index addresses the tree" in out, out
    rc, out = hd("run", 'tap "NoSuchNodeAnywhereXYZ"; key back')
    assert rc != 0 and "batch stopped at step 1" in out, out
    print("contract: bad verb rejected, non-first index rejected, failed step stops the "
          "batch and exits nonzero")


def run_flow(app, pkg, steps, verify):
    launch(pkg)
    hd("see")  # the setup look both variants start from
    singles_bytes, ok_s = 0, False
    for i, s in enumerate(steps):
        rc, out = hd(*split_step(s))
        singles_bytes += len(out)
        if i == len(steps) - 1:
            ok_s = re.search(verify, out) is not None
            if not ok_s:  # the fold may have printed a diff; buy the look an agent would
                rc, out = hd("find", verify)
                singles_bytes += len(out)
                ok_s = re.search(verify, out) is not None
    time.sleep(2)
    rc, out = hd("run", "; ".join(steps), "--find", verify)
    batch_bytes = len(out)
    ok_b = rc == 0 and re.search(verify, out) is not None
    return (len(steps), singles_bytes, ok_s), (1, batch_bytes, ok_b)


def split_step(s):
    return shlex.split(s)


def main():
    contract_checks()
    tot_sc = tot_sb = tot_bb = fails = 0
    n = 0
    for app, (pkg, steps, verify) in APPS.items():
        (sc, sb, ok_s), (bc, bb, ok_b) = run_flow(app, pkg, steps, verify)
        status = "ok" if ok_s and ok_b else "FAIL"
        if status == "FAIL":
            fails += 1
        print(f"{app:9s} singles: {sc} cmds {sb:6d}B   batch: {bc} cmd {bb:6d}B   "
              f"verify singles={ok_s} batch={ok_b} {status}")
        tot_sc += sc
        tot_sb += sb
        tot_bb += bb
        n += 1
    print(f"TOTAL     singles: {tot_sc} cmds {tot_sb}B   batch: {n} cmds {tot_bb}B   "
          f"({tot_sc / n:.1f}x fewer commands, {100 * (1 - tot_bb / tot_sb):.0f}% fewer bytes)")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
