# android-hybrid-navigation vs. unguided agent — 24-run blinded eval

**Matrix.** 6 apps x 2 arms x 2 replicates = 24 child sessions, Normal
capability, ~30 machine-verifiable tasks per app, one app per session. Apps:
amaze, joplin, lesspass, markor, seal, unitto. Every run booted the same emulator snapshot (Android 14, API 34, 720x1280
@320dpi, F-Droid APKs preinstalled) and ended with a fixed `adb` state dump, so grading is not
self-report. Arms were blind: hybrid sessions were told only to use whatever tooling they have;
bare sessions were forbidden from reading or invoking the skill.

## What the bare arm actually does

**Mostly it IS screenshot-driven CUA.** Denied the skill, agents sometimes reinvent it — a bare session may write a
`uiautomator dump` wrapper (`ui.sh`, `t.sh`, `ui.py`) in its first minute and grep it — and
sometimes just looks at the screen. Counting a run as *improvised tree tooling* at
<= 5 screenshots and as *visual CUA* at >= 20: 2/12 bare runs
improvised tree tooling, 6/12 did visual CUA,
4 sat in between. Median bare run:
22 screenshots across ~30 tasks. So this mostly measures **the skill vs. visual computer use**, the comparison the plugin README claims — and it is the flattering framing, not the harsh one. Re-check
this split every run before quoting the numbers; it decides which experiment you ran, and it
has flipped between runs of the same matrix.

The opposite failure — completing tasks by writing device state instead of driving the UI
(`adb shell mkdir` for "create a folder") — is counted too: runs touching device state directly,
6/12 hybrid vs 5/12
bare. A large imbalance here invalidates the ACU comparison, because one arm is doing less work.

## Headline

| metric | arm | mean | median | cv | p90 | max |
|---|---|---|---|---|---|---|
| ACU | hybrid | 11.9 | 12.1 | 0.36 | 14.7 | 19.4 |
| ACU | bare | 12.6 | 12.3 | 0.46 | 15.9 | 22.4 |
| perception tokens | hybrid | 33,609 | 34,424 | 0.30 | 39,350 | 50,815 |
| perception tokens | bare | 66,252 | 61,990 | 0.72 | 82,775 | 173,869 |
| screenshots | hybrid | 4 | 4 | 0.55 | 6 | 10 |
| screenshots | bare | 33 | 22 | 1.05 | 49 | 111 |
| tasks done (of ~30) | hybrid | 28.0 | 28.0 | 0.04 | 29.0 | 30.0 |
| tasks done (of ~30) | bare | 27.8 | 28.0 | 0.04 | 29.0 | 29.0 |

Hybrid/bare ratios: ACU **0.95x**, perception tokens
**0.51x**, iterations **0.99x**, exec calls
**1.20x**, tasks done **1.01x**.

Worst run by perception tokens — hybrid 50,815 (amaze|hybrid|1),
bare 173,869 (markor|bare|2).


### ACU by stack

| stack | hybrid mean | cv | bare mean | cv | hybrid/bare |
|---|---:|---:|---:|---:|---:|
| compose | 11.6 | 0.17 | 11.8 | 0.34 | 0.99x |
| rn | 8.0 | 0.44 | 9.0 | 0.59 | 0.89x |
| views | 16.1 | 0.18 | 17.0 | 0.36 | 0.95x |
| **all** | 11.9 | 0.36 | 12.6 | 0.46 | 0.95x |

### Perception tokens by stack

| stack | hybrid mean | cv | bare mean | cv | hybrid/bare |
|---|---:|---:|---:|---:|---:|
| compose | 35,100 | 0.09 | 58,854 | 0.34 | 0.60x |
| rn | 24,505 | 0.44 | 63,992 | 0.90 | 0.38x |
| views | 41,222 | 0.18 | 75,911 | 0.87 | 0.54x |
| **all** | 33,609 | 0.30 | 66,252 | 0.72 | 0.51x |

### Iterations by stack

| stack | hybrid mean | cv | bare mean | cv | hybrid/bare |
|---|---:|---:|---:|---:|---:|
| compose | 160 | 0.15 | 156 | 0.23 | 1.02x |
| rn | 112 | 0.35 | 127 | 0.54 | 0.88x |
| views | 211 | 0.17 | 202 | 0.25 | 1.04x |
| **all** | 161 | 0.32 | 162 | 0.36 | 0.99x |

### Screenshots by stack

| stack | hybrid mean | cv | bare mean | cv | hybrid/bare |
|---|---:|---:|---:|---:|---:|
| compose | 4 | 0.29 | 28 | 0.31 | 0.16x |
| rn | 2 | 0.43 | 37 | 1.11 | 0.06x |
| views | 6 | 0.41 | 35 | 1.47 | 0.19x |
| **all** | 4 | 0.55 | 33 | 1.05 | 0.13x |

### Tasks done (of ~30) by stack

| stack | hybrid mean | cv | bare mean | cv | hybrid/bare |
|---|---:|---:|---:|---:|---:|
| compose | 27.2 | 0.04 | 27.0 | 0.05 | 1.01x |
| rn | 28.8 | 0.04 | 28.2 | 0.03 | 1.02x |
| views | 28.0 | 0.00 | 28.2 | 0.02 | 0.99x |
| **all** | 28.0 | 0.04 | 27.8 | 0.04 | 1.01x |

### ACU by app

| app | hybrid mean | cv | bare mean | cv | hybrid/bare |
|---|---:|---:|---:|---:|---:|
| amaze | 18.5 | 0.07 | 17.5 | 0.38 | 1.06x |
| joplin | 10.7 | 0.22 | 13.3 | 0.27 | 0.80x |
| lesspass | 5.3 | 0.25 | 4.8 | 0.06 | 1.12x |
| markor | 13.8 | 0.10 | 16.6 | 0.50 | 0.83x |
| seal | 13.1 | 0.13 | 14.6 | 0.03 | 0.90x |
| unitto | 10.2 | 0.03 | 9.0 | 0.44 | 1.14x |
| **all** | 11.9 | 0.36 | 12.6 | 0.46 | 0.95x |

### Perception tokens by app

| app | hybrid mean | cv | bare mean | cv | hybrid/bare |
|---|---:|---:|---:|---:|---:|
| amaze | 46,556 | 0.13 | 48,447 | 0.33 | 0.96x |
| joplin | 32,598 | 0.22 | 109,976 | 0.35 | 0.30x |
| lesspass | 16,412 | 0.32 | 18,008 | 0.24 | 0.91x |
| markor | 35,888 | 0.12 | 103,375 | 0.96 | 0.35x |
| seal | 36,352 | 0.12 | 70,800 | 0.03 | 0.51x |
| unitto | 33,848 | 0.07 | 46,908 | 0.53 | 0.72x |
| **all** | 33,609 | 0.30 | 66,252 | 0.72 | 0.51x |

### Billed input tokens (what ACU tracks)

| | hybrid | bare |
|---|---:|---:|
| billed input, median | 12.69 Mtok | 12.19 Mtok |
| billed input, mean | 12.39 Mtok | 11.72 Mtok |
| peak resident context | 118,110 | 103,278 |
| turns | 161 | 162 |
| perception tokens | 33,609 | 66,252 |

Billed input is the integral of context size over turns, so a token added at turn *i* is charged again at every turn after it. Hybrid/bare on the median run: **1.04x** — a perception ratio of 0.51x does not carry into cost, because a whole run's perception spend is ~0.26% of what it bills.

### Which observation verb the hybrid arm typed

| verb | calls | share |
|---|---:|---:|
| `hd see --no-diff (opt out of the delta)` | 717 | 55% |
| `hd see --find` | 410 | 32% |
| `hd see (delta on a re-observation)` | 130 | 10% |
| `hd see --full` | 36 | 3% |
| `hd see -q (capture, print nothing)` | 4 | 0% |

## Method notes

- Perception tokens come from each session's final `context_growth_update` event
  (`approx_ant_tokens` per tool, plus image tokens for screenshots) — measured, not estimated
  from transcripts, and identical bookkeeping for both arms.
- Spread is the coefficient of variation: the arms differ in scale, so an absolute SD would
  flatter whichever arm is cheaper.
- Some suites cap below 30/30 in BOTH arms because the remaining tasks need an account or a
  network service (Jerboa needs a Lemmy login). That is the suite's ceiling, not an arm failing.
- Raw data: `runs.json` (cell -> session), `metrics.json`, `tasks.json`, `bypass.json`.

