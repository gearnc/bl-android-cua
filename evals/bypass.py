"""Detect runs that completed tasks by writing device state directly instead of driving the UI.

Both arms can reach the emulator's shell, so a task like "create a folder in the file manager"
can be satisfied with `adb shell mkdir` and never touch the app. That still passes the final
state dump, so it has to be counted before any ACU comparison means anything: an arm that
shortcuts is doing strictly less work.

Pure matching over the exec command strings; the caller collects them.
"""
import re

# Writes to device storage / app databases that are not input events.
WRITE = re.compile(
    r"adb\s+(?:-\w+\s+)?shell\s+(?:.*\s)?(mkdir|touch|rm\s|mv\s|cp\s|echo\s.*>|cat\s*>|sqlite3|"
    r"content\s+insert|pm\s+clear|settings\s+put)|adb\s+push\b", re.I)
# Deep-links / intents that jump the agent past navigation.
INTENT = re.compile(r"adb\s+(?:-\w+\s+)?shell\s+am\s+start[^|;]*(-e\s|--es\s|-d\s)", re.I)
# Reading app state from disk rather than the screen.
READ_DISK = re.compile(
    r"adb\s+(?:-\w+\s+)?shell\s+(?:.*\s)?(cat|sqlite3|ls)\s+[^|;]*(/data/data|/sdcard)", re.I)


def classify(cmds, dump_cmd=""):
    """Counts of shortcut commands, ignoring the mandated final verification dump."""
    n = dict(writes=0, intents=0, disk_reads=0)
    for c in cmds:
        if dump_cmd and dump_cmd[:40] in c:
            continue
        if WRITE.search(c):
            n["writes"] += 1
        if INTENT.search(c):
            n["intents"] += 1
        if READ_DISK.search(c):
            n["disk_reads"] += 1
    return n
