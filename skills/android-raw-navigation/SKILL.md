---
name: android-raw-navigation
description: The bare-hands method for driving an Android emulator/device efficiently with nothing but adb and a 30-line uiautomator-dump wrapper — read the tree, chain input actions, look once per command, verify by machine. Use when driving an Android app UI without the android-hybrid-navigation skill.
---

# Raw Android navigation: the method, not a tool

This skill is a *method*. It hands you nothing but the working pattern that unaided agents
independently rediscover — unreliably, and at the cost of the turns spent rediscovering it —
in every measured run: a `uiautomator dump` wrapper written in the first minute, then long
chains of `adb shell input` actions with one look at the end. Distilled from the
cheapest bare-arm transcripts of the 2026-08 A/B/C evals (the best run drove a full 30-task
suite in 57 shell commands), where the expensive runs were the ones that fell back to
screenshot-driving (145 screenshots, 239k perception tokens on the same suite).

Four rules, in order of how much they save:

## 1. Write the dump wrapper ONCE, first thing

Do not perceive by screenshot and do not type raw `uiautomator dump | grep` pipelines all
session. Write this once (e.g. to `~/ui.py`) and use it for every look:

```python
#!/usr/bin/env python3
"""ui.py — see [REGEX]: print the interactive/texted nodes of the current screen."""
import re, subprocess, sys
import xml.etree.ElementTree as ET

subprocess.run(["adb", "shell", "uiautomator", "dump", "/sdcard/ui.xml"],
               capture_output=True)
xml = subprocess.run(["adb", "shell", "cat", "/sdcard/ui.xml"],
                     capture_output=True, text=True).stdout
pat = re.compile(sys.argv[2], re.I) if len(sys.argv) > 2 else None
for n in ET.fromstring(xml).iter("node"):
    t = n.get("text") or n.get("content-desc")
    if n.get("clickable") != "true" and n.get("scrollable") != "true" and not t:
        continue
    x1, y1, x2, y2 = map(int, re.findall(r"-?\d+", n.get("bounds")))
    line = (f'{n.get("class").split(".")[-1]} "{t or ""}" '
            f'{"C" if n.get("clickable") == "true" else ""}'
            f'{"S" if n.get("scrollable") == "true" else ""} '
            f"({(x1 + x2) // 2},{(y1 + y2) // 2})")
    if not pat or pat.search(line):
        print(line)
```

`python3 ~/ui.py see` prints every actionable/texted node with its tap point;
`python3 ~/ui.py see 'Save'` is a grep-grade single lookup. That is the whole perception
layer. Take a screenshot only when the question is genuinely visual (a colour, an image,
a drawing) — if a task takes more than a couple of screenshots you are on the wrong layer.

## 2. Chain actions; pay for ONE look per command, at the end

You are billed per command (turn), not per byte. The single biggest cost difference between
cheap and expensive runs is actions-per-look: the cheap runs chained ~9 actions per look.
Put the whole step sequence and its one verification in one shell command:

```bash
adb shell input tap 360 340 && adb shell input text 'example.com' && \
adb shell input tap 360 462 && adb shell input text 'alice' && \
adb shell input tap 360 898; sleep 2; python3 ~/ui.py see 'Generated|error'
```

- `sleep 1`–`sleep 2.5` between taps that change screens; nothing between taps on a form
  you have already read.
- Coordinates come from your last `ui.py` look; anything that opens/closes a dialog,
  keyboard, menu or screen moves them — re-look after such a step, inside the same command.
- `adb shell input text` needs spaces as `%s` and lands in the focused field;
  `adb shell input keyevent 4` = back, `66` = enter, `67` = backspace,
  `adb shell input swipe X1 Y1 X2 Y2 300` scrolls.

## 3. Script any flow you do more than twice

The second time you do the same flow (set a field and regenerate, add another item), put the
tap/type sequence in a two-line shell script with the varying part as `$1`, and replay it.
The cheapest measured run drove most of its suite through two such helpers.

## 4. Verify by machine, not by eyes

One verification per task, and prefer a machine check to any look:
`adb shell settings get ...`, `adb shell content query ...`, `adb shell ls ...`,
`adb shell dumpsys ...`, or `ui.py see 'PAT'` for on-screen state. Never verify by
screenshot what a grep can prove.

## Known traps

- The soft keyboard covers the bottom half of the screen and shifts everything above it:
  after focusing a field, either type immediately (`input text` works with the IME up) or
  dismiss it (`input keyevent 111`) before tapping by coordinate again.
- `uiautomator dump` returns the *current* window — a toast or transient dialog can occupy
  it; re-dump after a `sleep` if the tree looks wrong.
- Fresh installs show onboarding screens; tap through them first, they are in the tree.
