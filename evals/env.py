"""Locating adb, hd.py and accessibility-cli on the eval box, without hard-coding a layout."""
import os
import shutil
from pathlib import Path

SDK = Path(os.environ.get("ANDROID_SDK_ROOT", Path.home() / "android-sdk"))
ADB = os.environ.get("HD_ADB") or shutil.which("adb") or str(SDK / "platform-tools/adb")
PATH = str(Path(ADB).parent) + os.pathsep + os.environ.get("PATH", "")
ENV = {**os.environ, "PATH": PATH}


def find_hd():
    """The skill's CLI: $HD_PY, else the copy in this repo, else wherever the plugin cache put it.

    $HD_PY lets a bench run against another revision of hd.py to show a fix actually changed it.
    """
    if os.environ.get("HD_PY"):
        return os.environ["HD_PY"]
    local = Path(__file__).resolve().parent.parent / "skills/android-hybrid-navigation/hd.py"
    if local.exists():
        return str(local)
    for root in (Path.home(), Path("/opt/.devin"), Path("/usr/local/share")):
        for p in root.rglob("android-hybrid-navigation/hd.py"):
            return str(p)
    raise FileNotFoundError("hd.py not found — is the plugin installed?")


def find_acli():
    """DioxusLabs/accessibility-cli: $ACLI_BIN, else PATH, else a cargo/target build."""
    if os.environ.get("ACLI_BIN"):
        return os.environ["ACLI_BIN"]
    found = shutil.which("accessibility-cli")
    if found:
        return found
    for p in (Path.home() / ".cargo/bin/accessibility-cli",
              Path.home() / "repos/accessibility-cli/target/release/accessibility-cli"):
        if p.exists():
            return str(p)
    raise FileNotFoundError("accessibility-cli not found — is it built into the snapshot?")
