---
name: android-hybrid-navigation
description: Token-efficient Android emulator/device navigation for agents — compact accessibility-tree perception with escalation, coordinate actions via adb, screenshots only for visual state. Use whenever driving an Android app UI.
---

# Android hybrid navigation (hd, framework-adaptive v5)

Navigate Android UIs by TEXT, not screenshots. A full screenshot costs ~1.5k tokens; a compact
tree view costs ~200–600. Use the bundled `hd.py` CLI (same directory as this skill) for both
perception and action — install it as `hd` with the one-time setup below. Fall back to
screenshots ONLY for visual-only state (colors/themes/images).

## Setup (once per session)
1. Ensure `adb` is on PATH and a device/emulator is connected (`adb devices`).
2. Install the `hd` launcher. Run this verbatim — it locates `hd.py` wherever the skill happens
   to be installed and drops a launcher in `/usr/local/bin`, which is on the default PATH.
   ```bash
   HD_PY=$(find "$HOME" /opt/.devin /usr/local/share -name hd.py -path '*android-hybrid-navigation*' -print -quit 2>/dev/null)
   printf '#!/usr/bin/env bash\nexec python3 "%s" "$@"\n' "$HD_PY" |
     sudo tee /usr/local/bin/hd >/dev/null && sudo chmod +x /usr/local/bin/hd
   hd see --find .   # prints the current screen's matching nodes; confirms adb + hd both work
   ```
   Do NOT use `alias hd=...`, and do not rely on `~/bin` + `~/.bashrc`: every command you run
   starts a fresh non-interactive shell, which reads neither. If `sudo` is unavailable, write
   the launcher to `$HOME/bin/hd` instead and prefix *each* later command with
   `export PATH="$HOME/bin:$PATH";`.
3. No device-side install is needed — perception uses `uiautomator dump`.
4. `hd see` auto-detects the foreground app's UI framework (Views / Compose / React Native)
   and tunes its output; the active profile is printed in the header line. Override with
   `HD_PROFILE=views|compose|rn` if detection looks wrong.

## Getting places cheaply: intent deep-links
Before navigating any system UI by hand, jump straight there with an intent — it costs one
step and zero perception:
`adb shell am start -a android.settings.AIRPLANE_MODE_SETTINGS` (likewise WIFI_SETTINGS,
DISPLAY_SETTINGS, TEXT_READING_SETTINGS, APPLICATION_DETAILS_SETTINGS …),
`am start -a android.intent.action.INSERT -t vnd.android.cursor.dir/contact -e name X -e phone Y`,
`am start -a android.intent.action.SENDTO -d sms:<number>`,
`am start -n <pkg>/<activity>` or `monkey -p <pkg> 1` to launch apps. Then `hd see` from there.

## Core loop (repeat per action)
1. `hd see` — read the indexed node list. Nodes show class, label, #resource-id,
   checked/selected state, `<C>`lickable/`<S>`crollable/`<E>`dit flags, and center coords.
   When you already know what you're after, use `hd see --find <regex>` instead — it prints
   only matching nodes (a few lines instead of the whole tree) with tappable indexes.
   **Printing a whole screen you did not need is the most expensive habit available to you.**
   For a single lookup `hd see --find PAT` is the cheapest thing there is. When you have several
   things to check on one screen, split capture from retrieval: `hd see -q` caches the full tree
   and prints one line, then each `hd find PAT` greps that cache with no new dump. Either way you
   pay for the matches, not the screen — 77% less printed output than reading the tree, measured
   over 4 apps in `evals/test_capture_retrieval.py`. If `hd find` reports NO MATCH, re-observe
   with `hd see` rather than guessing again.
2. Act: `hd tap <index>` (verifies the node is still where you saw it), `hd longpress <index>`,
   `hd type "text"`, `hd key back|enter|...`, `hd swipe up|down`.
   **When the action needs a look after it, add `-s` instead of running one.** Every action verb
   takes `-s [PAT]`: it does the action, waits for the screen to settle, then prints exactly what
   the next `hd see` (or `hd see --find PAT`) would have printed. `hd tap 5 -s` is one command
   where `hd tap 5` + `sleep 2` + `hd see` is two, for the same bytes — and you are billed per
   command, not per byte. Wherever this skill says "re-`see`", "verify" or "confirm" after an
   action, that means `-s` on the action, not a second command.
   **Per-item actions (rename/delete/copy/move on a list item, file, feed, note): long-press
   the item FIRST** — Android puts these in a context menu or selection-mode toolbar opened by
   long-press. Do not hunt for an edit button or overflow menu until a long-press has failed.
   Long-press with `-s` (`hd longpress 7 -s`) — look for a selection toolbar (often icon-only;
   the three-dot "More options" node reveals labeled Rename/Copy entries).
3. Re-observe when the screen may have changed shape — but NOT reflexively, and not as its own
   command when `-s` on the action would have done it. Pick the cheapest observation that
   answers your actual question:
   - **You know what you're checking** → `hd see --find PAT`, or `hd see -q` once and then a
     `hd find PAT` per thing you want to confirm.
   - **Otherwise just run `hd see`.** A re-`see` of a screen you already observed prints only
     the nodes that appeared or disappeared since the last tree it actually printed to you
     (a `--find` or `-q` in between changes nothing: you were never shown their tree, so it is
     not what the delta is against), with
     current indexes, so `hd tap` works straight off it. Measured over 24 post-action
     observations across 8 apps this cuts the observation by 69% on average, 96–97% when a tap
     only changed a toolbar or a row's state. When the screen turns over entirely, or the last
     `see` is more than 120s old, you get the whole tree — so it is never a trap and there is
     no flag to remember, and nothing to opt out of: a delta already carries current indexes,
     so re-reading the whole tree after a tap buys nothing you did not already have.
   See "Earned shortcuts" below for when to skip the re-observation altogether. A standalone
   observation is worth its own turn only when you are not acting: deciding what to do next on a
   screen you have not seen, or checking an end state no action of yours just produced.

## Earned shortcuts: don't pay for certainty you already have
The observe→act→observe loop is the safe default, but on screens you have ALREADY observed
and that cannot shift, skip the extra looks:
- **Batch actions on stable layouts.** A form whose fields you've already indexed doesn't
  need a re-`see` between filling field 1 and field 2: `hd tap 5 && hd type "x" && hd tap 7
  && hd type "y" -s` in one step — the trailing `-s` verifies both landed without a second
  call. Same for a known row of checkboxes, +/- steppers (`hd tap 9; hd tap 9; hd tap 9 -s`),
  or dismissing a familiar dialog.
- **Reuse coordinates for repeated flows.** Doing the same flow the 2nd/3rd time (add another
  card, create another note): replay the taps with `hd tap-xy` from your notes and verify only
  the END state, not each step.
- **Skip re-see after typing** when the field was focused and `hd type` echoed success — fold
  the verification into your next action's `-s` instead of adding an observation.
- **One verification per task, not per action**, whenever a single `see --find` (or adb check
  — `ls`, `settings get`, `content query`) can prove the whole task's end state.
Do NOT batch across layout changes: anything that opens/closes a dialog, keyboard, menu,
screen, or selection mode invalidates indexes and coordinates — re-observe first. If a
batched sequence produces a surprise (`hd tap` says "node moved/gone"), stop and re-`see`.

## Framework-adaptive observation: pick the primitive by profile
The header of every `hd see` prints the detected profile. Use a DIFFERENT default primitive
per profile — this is the core of the skill:

```
profile=views    hd see --find <target>     grep-grade cost; trees are labeled, so a
                 (default primitive)        pattern almost always hits. Fall back to
                                            plain `hd see` only when exploring a new screen.
profile=compose  hd see (arrival prints     unlabeled clickable Views are only findable via
                 the tree, re-see prints    their near:"label" hints, which plain grep-style
                 the delta)                 thinking would miss — so the rendered tree is the
                                            primitive the FIRST time you meet a screen, and a
                                            re-`see` costs only the delta. Re-reading a whole
                                            tree after every tap is the most expensive habit
                                            in this profile — take the delta.
profile=rn       hd see --find <target>     labels usually hit; --find also matches state
                 then `hd see` on miss      (e.g. --find 'checked=false' lists unchecked
                                            boxes). Re-tap by coords if a tap no-ops.
```

Escalation (any profile): --find NO MATCH is not proof of absence → plain `hd see` →
`hd see --full` (every node; auto-triggered when compact yields <5) → `hd shot x.png` + view.
Screenshots are required only for: theme/color verification, unlabeled icon disambiguation,
canvas/WebView pixels, or when `uiautomator dump` keeps failing on animated screens.

## Framework-specific traps
- **Views**: richest trees; permission dialogs and menus all greppable. Cheapest case.
- **Compose** (profile=compose): switches are bare `View`s, but they carry state and the tree
  shows it as `checked=true/false` on the row — read that, never a screenshot. Some settings
  also state themselves as text ("On"/"Use device theme"); toggle with `hd tap N -s checked`. Some
  Compose checkboxes ignore `input tap` — if state didn't change after 2 attempts, verify
  another way instead of looping. Back button may CANCEL an edit screen instead of saving —
  look for an explicit OK/Save node.
- **RN** (profile=rn): tap by index/coords only (tree-issued a11y clicks can silently no-op —
  tap with `-s` so the confirmation costs no extra call). Checkable nodes always show `checked=true/false`
  — trust it over a screenshot, and `--find 'checked=false'` lists the unchecked ones. Note
  editors are often WebViews: their EditTexts usually still
  accept `hd type` after a tap; verify with `hd type "x" -s` before reaching for a screenshot.

## Typing
`hd type` injects text below the IME — it always reaches the field even when host keystrokes
don't. Tap the target field with `-s` to confirm focus/content in the same call, then type with
`-s` to see the text land; retype the missing part if it didn't. Two commands for the whole
field, not four.

## Verification
Prefer machine checks over screenshots: file contents via `adb shell cat`, settings via
`adb shell settings get`, content providers via `adb shell content query`, and tree state via
`hd see`. Budget rule of thumb: if a task takes >5 screenshots, you're using the wrong layer.

## Common traps
- First-launch ANR dialogs ("app isn't responding") right after emulator boot: tap Wait, sleep
  30–60 s; if it persists, `adb shell am force-stop <pkg>` and relaunch.
- Permission walls: grant via adb when allowed (`adb shell appops set <pkg>
  MANAGE_EXTERNAL_STORAGE allow`, `pm grant`) instead of navigating Settings UI.
- "Mark all"-type actions may be scoped to the current view — verify globally.
- After theme changes the activity restarts; observe from scratch (`hd see`), and expect a whole
  tree rather than a delta.
