"""Check every suite's verification dump runs clean against the live emulator.

A dump that errors silently turns grading into self-report, so this runs before any matrix.
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from env import ADB  # noqa: E402
from suites import APPS  # noqa: E402

BAD = ("not found", "syntax error", "Permission denied")

# The playbook's preflight condition is "rc=0 with no problems for every app", but printing the
# return code and exiting 0 anyway made that condition unenforceable: the 16 Aug matrix launched
# with several apps' dumps exiting non-zero and the caveat only surfaced in the report.
failed = []
for k, a in APPS.items():
    r = subprocess.run([ADB, "shell", a["dump"]], capture_output=True, timeout=180)
    out = r.stdout.decode(errors="replace") + r.stderr.decode(errors="replace")
    bad = [ln for ln in out.splitlines() if any(b in ln for b in BAD)]
    print(f"{k:17s} rc={r.returncode} bytes={len(out):6d} problems={bad[:2]}")
    if r.returncode or bad:
        failed.append(k)

if failed:
    sys.exit(f"\ndump preflight FAILED for {', '.join(failed)} — grading would be self-report "
             f"for those apps. Fix the dump (or the app's fixture state) before launching.")
print("\nall suite dumps clean  OK")
