"""Locating adb and hd.py on the eval box, without hard-coding one machine's layout."""
import os
import shutil
from pathlib import Path

SDK = Path(os.environ.get("ANDROID_SDK_ROOT", Path.home() / "android-sdk"))
ADB = os.environ.get("HD_ADB") or shutil.which("adb") or str(SDK / "platform-tools/adb")
PATH = str(Path(ADB).parent) + os.pathsep + os.environ.get("PATH", "")
ENV = {**os.environ, "PATH": PATH}


def find_hd():
    """The skill's CLI: the copy in this repo if present, else wherever the plugin cache put it."""
    local = Path(__file__).resolve().parent.parent / "skills/android-hybrid-navigation/hd.py"
    if local.exists():
        return str(local)
    for root in (Path.home(), Path("/opt/.devin"), Path("/usr/local/share")):
        for p in root.rglob("android-hybrid-navigation/hd.py"):
            return str(p)
    raise FileNotFoundError("hd.py not found — is the plugin installed?")
