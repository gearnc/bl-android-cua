# android-hybrid-navigation vs. unguided agent — 24-run blinded eval

**Matrix.** 6 apps x 2 arms x 2 replicates = 24 child sessions, Normal
capability, ~30 machine-verifiable tasks per app, one app per session. Apps:
amaze, joplin, lesspass, markor, seal, unitto. Every run booted the same emulator snapshot (Android 14, API 34, 720x1280
@320dpi, F-Droid APKs preinstalled) and ended with a fixed `adb` state dump, so grading is not
self-report. Arms were blind: hybrid sessions were told only to use whatever tooling they have;
bare sessions were forbidden from reading or invoking the skill.

## What the bare arm actually does

**Mostly it is not screenshot-driven CUA.** Denied the skill, agents reinvent it: a typical bare
session writes a `uiautomator dump` wrapper (`ui.sh`, `t.sh`, `ui.py`) in its first minute and
greps it. Counting a run as *improvised tree tooling* at <= 5 screenshots and as *visual
CUA* at >= 20: 5/12 bare runs improvised tree tooling,
2/12 did visual CUA, 5 sat in between. Median bare run:
11 screenshots across ~30 tasks. So this mostly
measures **the skill vs. agent-improvised tree tooling**, not the skill vs. looking at the
screen — and the bare arm's tail is dominated by the runs that fell back to pixels. Re-check
this split every run before quoting the numbers; it decides which experiment you ran.

The opposite failure — completing tasks by writing device state instead of driving the UI
(`adb shell mkdir` for "create a folder") — is counted too: runs touching device state directly,
1/12 hybrid vs 4/12
bare. A large imbalance here invalidates the ACU comparison, because one arm is doing less work.

## Headline

| metric | arm | mean | median | cv | p90 | max |
|---|---|---|---|---|---|---|
| acu | hybrid | 13 | 14 | 0.34 | 17 | 21 |
| acu | bare | 13 | 12 | 0.25 | 15 | 22 |
| perception_tokens | hybrid | 22,305 | 14,211 | 0.94 | 20,559 | 79,176 |
| perception_tokens | bare | 44,624 | 25,100 | 1.30 | 32,624 | 185,883 |
| screenshots | hybrid | 6 | 4 | 1.66 | 7 | 33 |
| screenshots | bare | 24 | 11 | 1.65 | 17 | 121 |
| n_done | hybrid | 28 | 28 | 0.03 | 29 | 30 |
| n_done | bare | 28 | 28 | 0.03 | 29 | 30 |

Hybrid/bare ratios: ACU **1.02x**, perception tokens
**0.50x**, iterations **1.00x**, exec calls
**1.28x**, tasks done **0.99x**.

Worst run by perception tokens — hybrid 79,176 (seal|hybrid|1),
bare 185,883 (amaze|bare|2).


### ACU by stack
stack               hybrid mean     cv    bare mean     cv   ratio
compose                      14   0.38           11   0.06    1.24
rn                           10   0.34           14   0.19    0.71
views                        17   0.10           15   0.33    1.15
ALL                          13   0.34           13   0.25    1.02

### Perception tokens by stack
stack               hybrid mean     cv    bare mean     cv   ratio
compose                   30938   1.05        18685   0.54    1.66
rn                        15911   0.13        58237   1.02    0.27
views                     20065   0.97        56951   1.51    0.35
ALL                       22305   0.94        44624   1.30    0.50

### Iterations by stack
stack               hybrid mean     cv    bare mean     cv   ratio
compose                     107   0.88           61   0.17    1.76
rn                           62   0.08          102   0.75    0.61
views                       111   0.81          116   0.88    0.96
ALL                          93   0.77           93   0.76    1.00

### Screenshots by stack
stack               hybrid mean     cv    bare mean     cv   ratio
compose                      11   1.33            6   1.05    1.73
rn                            3   0.46           34   1.16    0.09
views                         2   1.68           32   1.88    0.06
ALL                           6   1.66           24   1.65    0.23

### Tasks done (of ~30) by stack
stack               hybrid mean     cv    bare mean     cv   ratio
compose                      28   0.02           28   0.02    1.00
rn                           29   0.03           29   0.03    1.00
views                        28   0.02           29   0.00    0.98
ALL                          28   0.03           28   0.03    0.99

### ACU by app
app                 hybrid mean     cv    bare mean     cv   ratio
amaze                        18   0.07           18   0.26    0.99
joplin                       12   0.14           14   0.30    0.88
lesspass                      7   0.13           13   0.11    0.53
markor                       16   0.08           11   0.05    1.41
seal                         17   0.29           11   0.10    1.61
unitto                       10   0.04           11   0.02    0.89
ALL                          13   0.34           13   0.25    1.02

### Perception tokens by app
app                 hybrid mean     cv    bare mean     cv   ratio
amaze                     30361   0.88       101586   1.17    0.30
joplin                    15898   0.18        86550   0.99    0.18
lesspass                  15925   0.14        29925   0.13    0.53
markor                     9768   0.01        12316   0.38    0.79
seal                      44562   1.10        10146   0.14    4.39
unitto                    17314   0.27        27224   0.15    0.64
ALL                       22305   0.94        44624   1.30    0.50

## Method notes

- Perception tokens come from each session's final `context_growth_update` event
  (`approx_ant_tokens` per tool, plus image tokens for screenshots) — measured, not estimated
  from transcripts, and identical bookkeeping for both arms.
- Spread is the coefficient of variation: the arms differ in scale, so an absolute SD would
  flatter whichever arm is cheaper.
- Some suites cap below 30/30 in BOTH arms because the remaining tasks need an account or a
  network service (Jerboa needs a Lemmy login). That is the suite's ceiling, not an arm failing.
- Raw data: `runs.json` (cell -> session), `metrics.json`, `tasks.json`, `bypass.json`.

