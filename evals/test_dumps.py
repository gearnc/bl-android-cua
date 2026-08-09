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

for k, a in APPS.items():
    r = subprocess.run([ADB, "shell", a["dump"]], capture_output=True, timeout=180)
    out = r.stdout.decode(errors="replace") + r.stderr.decode(errors="replace")
    bad = [ln for ln in out.splitlines() if any(b in ln for b in BAD)]
    print(f"{k:17s} rc={r.returncode} bytes={len(out):6d} problems={bad[:2]}")
