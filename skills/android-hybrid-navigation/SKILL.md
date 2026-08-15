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

## Core loop (once per TASK, not once per action)
1. `hd see` — read the indexed node list. Nodes show class, label, #resource-id,
   checked/selected state, `<C>`lickable/`<S>`crollable/`<E>`dit/`<F>`ocused flags, and center
   coords.
   When you already know what you're after, use `hd see --find <regex>` instead — it prints
   only matching nodes (a few lines instead of the whole tree) with tappable indexes.
   **Printing a whole screen you did not need is the most expensive habit available to you.**
   For a single lookup `hd see --find PAT` is the cheapest thing there is. When you have several
   things to check on one screen, split capture from retrieval: `hd see -q` caches the full tree
   and prints one line, then each `hd find PAT` greps that cache with no new dump. Either way you
   pay for the matches, not the screen — 77% less printed output than reading the tree, measured
   over 4 apps in `evals/test_capture_retrieval.py`. Neither verb makes you pay twice for a
   miss: `hd see --find` and `hd find` both print the tree they matched against when the
   pattern hits nothing, with the indexes `hd tap` expects, so a miss costs one look.
2. Act: `hd tap <index>` (verifies the node is still where you saw it), `hd longpress <index>`,
   `hd type "text"`, `hd key back|enter|...`, `hd swipe up|down`.
   **When you can already name the target, tap it by name and skip step 1 entirely**:
   `hd tap "Save"` matches the same regex `--find` does, observes the screen itself if its
   cached tree is stale, and taps the node — one turn where a look plus a tap was two.
   In the 2026-08-15 A/B/C at `b3898c3`, 100 of the hybrid arm's 252 look-only commands existed
   for nothing but to turn a label into an index while the pattern form took only 16% of taps, so
   `hd tap <index>` now says so itself — once a session, after an index tap that a standalone look
   preceded, naming the pattern that would have skipped it; over the six default apps the pattern form lands on the
   same node as the index form 16/16 times at 50% of the turns and 24% of the printed bytes
   (`evals/test_tap_label.py`). If the name is ambiguous it taps NOTHING and prints the
   candidates with their indexes, so choosing still costs no extra look. Use an index when you
   are already holding a tree, a name when you are not.
   **Every action observes after itself — you never run a `see` to find out what an action did.**
   The verb waits for the screen to settle and prints what the next `hd see` would have; `-s PAT`
   narrows that to what `hd see --find PAT` would. Wherever this skill says "re-`see`", "verify"
   or "confirm" after an action, it means that built-in look, never a second command.
   **Chain the actions you already have indexes for and let only the LAST one look**, with `-n`
   on the others:

   ```
   hd tap 5 -n; hd type "Groceries" -n; hd tap 12          # one turn, one tree at the end
   ```

   You are billed per command, not per byte: one 8-action command that looks once is a fraction
   of the cost of 8 that look 8 times. In the 2026-08-11 A/B/C the skill printed 0.67x the
   perception tokens of an unaided agent and still cost 1.10x its ACU, purely because it looked
   3.26 times per task against that agent's 1.96 — the unaided agent chained 8.74 actions per
   look. Measured across those 24 cells, one extra look per task costs 0.078 ACU per task.
   **Per-item actions (rename/delete/copy/move on a list item, file, feed, note): long-press
   the item FIRST** — Android puts these in a context menu or selection-mode toolbar opened by
   long-press. Do not hunt for an edit button or overflow menu until a long-press has failed.
   Its own look shows you the result — look for a selection toolbar (often icon-only;
   the three-dot "More options" node reveals labeled Rename/Copy entries).
3. A STANDALONE `hd see` is for a screen no action of yours just produced — arriving somewhere,
   or checking an end state. After your own action, the look is already in the command. When you
   do need one, pick the cheapest observation that answers your actual question:
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
   See "Earned shortcuts" below for when to skip the look altogether with `-n`.

## Earned shortcuts: don't pay for certainty you already have
The observe→act→observe loop is the safe default, but on screens you have ALREADY observed
and that cannot shift, skip the extra looks:
- **Batch actions on stable layouts.** A form whose fields you've already indexed doesn't
  need a look between filling field 1 and field 2: `hd tap 5 -n; hd type "x" -n; hd tap 7 -n;
  hd type "y"` in one step — the last action's own look verifies all four landed. Same for a
  known row of checkboxes, +/- steppers (`hd tap 9 -n; hd tap 9 -n; hd tap 9`), or dismissing a
  familiar dialog (`hd tap 3 -n`, and see it on your next action).
- **Reuse coordinates for repeated flows.** Doing the same flow the 2nd/3rd time (add another
  card, create another note): replay the taps with `hd tap-xy -n` from your notes and verify only
  the END state, not each step.
- **Skip the look after typing** when the field was focused and `hd type` echoed success —
  `hd type "x" -n`, and let your next action's look cover it.
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

Escalation (any profile): a NO MATCH is not proof of absence, and it hands you the tree so you
can see for yourself → `hd see --full` (every node; auto-triggered when compact yields <5) →
`hd shot x.png` + view.
Screenshots are required only for: theme/color verification, unlabeled icon disambiguation,
canvas/WebView pixels, or when `uiautomator dump` keeps failing on animated screens.

## Framework-specific traps
- **Views**: richest trees; permission dialogs and menus all greppable. Cheapest case.
- **Compose** (profile=compose): switches are bare `View`s, but they carry state and the tree
  shows it as `checked=true/false` on the row — read that, never a screenshot. Some settings
  also state themselves as text ("On"/"Use device theme"); toggle with `hd tap N -s checked`,
  whose look is the one line that proves it flipped. Some
  Compose checkboxes ignore `input tap` — if state didn't change after 2 attempts, verify
  another way instead of looping. Back button may CANCEL an edit screen instead of saving —
  look for an explicit OK/Save node.
- **RN** (profile=rn): tap by index/coords only (tree-issued a11y clicks can silently no-op —
  the tap's own look is your confirmation, so do NOT `-n` a tap you are unsure of). Checkable
  nodes always show `checked=true/false` — trust it over a screenshot, and `--find 'checked=false'`
  lists the unchecked ones. Note editors are often WebViews: their EditTexts usually still
  accept `hd type` after a tap; read the type's own look before reaching for a screenshot.

## Typing
`hd type` injects text below the IME — it always reaches the field even when host keystrokes
don't. `hd tap <field> -n; hd type "text"` is the whole thing in one turn: the type's own look
shows the text landed, so retype only the missing part if it didn't.

**A field that already has a value needs `-r`, not a backspace loop.** `hd type "new" -r` reads
the focused field's current length off the tree and deletes exactly that many characters before
typing — including a password field, whose bullets it counts. Never hand-roll
`for i in $(seq 30); do adb shell input keyevent 67; done`: you do not know the length, and a
wrong guess either fuses the tail of the old value onto the new one or costs another turn to
find out. `hd clear` is the same deletion with nothing typed after it.

Both act on the **focused** field, which the tree marks `<F>`: if `--find EditText` shows a field
without it, your tap did not land in it, and `hd type ... -r` will say so and list the indexes
that do focus one — tap one of those rather than grepping the tree for the field.

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
