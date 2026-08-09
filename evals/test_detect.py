"""Regression check for hd.py profile detection across every app in the eval matrix.

Compares detected profile against the expected label in suites.APPS (which was set from the
runtime tree observed by hand, not from APK contents). Clears the per-package cache first.
"""
import json, os, subprocess, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from env import ENV as env, find_hd  # noqa: E402
from suites import APPS  # noqa: E402

HD = sys.argv[1] if len(sys.argv) > 1 else find_hd()


def adb(*a, **kw):
    return subprocess.run(["adb", *a], capture_output=True, text=True, env=env, **kw).stdout


def main():
    if os.path.exists("/tmp/hd_fw_cache.json"):
        os.remove("/tmp/hd_fw_cache.json")
    rows, bad = [], 0
    for key, app in APPS.items():
        pkg = app["pkg"]
        adb("shell", "monkey", "-p", pkg, "1")
        time.sleep(7)
        out = subprocess.run([sys.executable, HD, "see"], capture_output=True, text=True,
                             env=env).stdout
        # `see` may print an auto-escalation notice before the header carrying profile=.
        header = next((l for l in out.splitlines() if "profile=" in l),
                      out.splitlines()[0] if out else "(no output)")
        got = "?"
        for p in ("compose", "rn", "views"):
            if f"profile={p}" in header:
                got = p
                break
        # Wikipedia's onboarding is genuinely ComposeView-rendered (unlabeled clickable Views
        # with near: hints) while the rest of the app is classic Views, so either is correct
        # on the launch screen.
        ok = got in (("compose", "views") if key == "wikipedia" else (app["stack"],))
        bad += not ok
        rows.append((key, app["stack"], got, "ok" if ok else "MISMATCH", header[:110]))
        adb("shell", "am", "force-stop", pkg)
    w = max(len(r[0]) for r in rows)
    for k, exp, got, verdict, hdr in rows:
        print(f"{k:<{w}}  expect={exp:<7} got={got:<7} {verdict}")
        if verdict != "ok":
            print(f"{'':<{w}}  {hdr}")
    print(f"\n{len(rows) - bad}/{len(rows)} correct")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
