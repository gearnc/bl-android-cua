# bl-android-cua

Devin skill plugin for token-efficient Android computer use (CUA).

## What's inside

- `skills/android-hybrid-navigation/` — the **android-hybrid-navigation** skill (v5):
  - `SKILL.md` — the agent-facing procedure: framework-adaptive accessibility-tree
    perception (Views / Jetpack Compose / React Native profiles), intent deep-links,
    coordinate actions via adb, long-press for per-item context menus, "earned shortcuts"
    (action batching on stable layouts, coordinate reuse), screenshots only for
    visual-only state.
  - `hd.py` — the bundled zero-dependency CLI (Python 3 stdlib + adb) the skill drives:
    `hd see [--full|--find PAT|-q]` (a re-`see` prints only the delta; `-q` caches
    the tree and prints nothing), `hd find PAT` (grep the cached tree, no new dump),
    `hd tap/longpress <index|"PAT">` (a name resolves against the tree, and an ambiguous one
    taps nothing and prints the candidates), `hd tap-xy/longpress-xy`,
    `hd type`, `hd key`, `hd swipe`, `hd shot`, `hd wait-idle`. Every action verb observes
    after acting by default — act, wait for the screen to settle, then print what the next
    `hd see` would have, in one command instead of two, because an agent is billed per turn
    and 96% of its taps are followed by a look. `-s PAT` narrows that look, `-n` drops it
    (what a batch wants on every action but its last).

## Install

```bash
devin plugins install COG-GTM/bl-android-cua
```

The skill is then available as `/android-cua:android-hybrid-navigation` and activates
whenever a session drives an Android app UI.

## Why

Blinded evals across Views/Compose/React Native apps showed this skill cuts estimated
perception tokens ~30% on average vs unguided native computer use, with ~3x tighter
run-to-run variance (worst-case run 14k vs 27k estimated tokens) at equal task reliability.

## Requirements

- `adb` on PATH with a connected device/emulator.
- Python 3 (stdlib only).
