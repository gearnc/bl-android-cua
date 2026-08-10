# android-hybrid-navigation vs. unguided agent vs. accessibility-cli — 36-run blinded eval

**Matrix.** 6 apps x 3 arms x 2 replicates = 36 child sessions,
Normal capability, ~30 machine-verifiable tasks per app, one app per session. Apps:
amaze, joplin, lesspass, markor, seal, unitto. Arms: hybrid, bare, acli. Every run booted the same emulator snapshot
(Android 14, API 34, 720x1280 @320dpi, F-Droid APKs preinstalled) and ended with a fixed `adb`
state dump, so grading is not self-report. Arms were blind and differ by exactly one paragraph:
hybrid was told only to use whatever tooling it has, bare was forbidden the skill, acli was forbidden the skill and pointed at the prebuilt `accessibility-cli` binary. Ratios are against **bare**.

## What the bare arm actually does

**Mostly it IS screenshot-driven CUA.** Denied the skill, agents sometimes reinvent it — a bare session may write a
`uiautomator dump` wrapper (`ui.sh`, `t.sh`, `ui.py`) in its first minute and grep it — and
sometimes just looks at the screen. Counting a run as *improvised tree tooling* at
<= 5 screenshots and as *visual CUA* at >= 20: 1/12 bare runs
improvised tree tooling, 4/12 did visual CUA,
7 sat in between. Median bare run:
10 screenshots across ~30 tasks. So this mostly measures **the skill vs. visual computer use**, the comparison the plugin README claims — and it is the flattering framing, not the harsh one. Re-check
this split every run before quoting the numbers; it decides which experiment you ran, and it
has flipped between runs of the same matrix.

The opposite failure — completing tasks by writing device state instead of driving the UI
(`adb shell mkdir` for "create a folder") — is counted too: runs touching device state directly,
6/12 hybrid, 7/12 bare, 6/12 acli.
A large imbalance here invalidates the ACU comparison, because one arm is doing less work.

## Headline

| metric | arm | mean | median | cv | p90 | max |
|---|---|---|---|---|---|---|
| ACU | hybrid | 13.0 | 12.6 | 0.40 | 17.0 | 21.2 |
| ACU | bare | 11.5 | 10.6 | 0.36 | 14.0 | 19.1 |
| ACU | acli | 14.9 | 14.1 | 0.38 | 16.9 | 26.5 |
| perception tokens | hybrid | 36,471 | 38,198 | 0.25 | 43,961 | 47,409 |
| perception tokens | bare | 49,522 | 39,248 | 0.56 | 67,824 | 118,178 |
| perception tokens | acli | 52,260 | 40,032 | 0.45 | 76,866 | 105,687 |
| screenshots | hybrid | 5.5 | 4.0 | 0.67 | 7.0 | 15.0 |
| screenshots | bare | 19.4 | 10.5 | 1.04 | 29.0 | 72.0 |
| screenshots | acli | 22.2 | 14.5 | 0.73 | 42.0 | 58.0 |
| tasks done (of ~30) | hybrid | 27.6 | 27.5 | 0.05 | 29.0 | 30.0 |
| tasks done (of ~30) | bare | 28.2 | 28.0 | 0.04 | 29.0 | 30.0 |
| tasks done (of ~30) | acli | 28.2 | 28.0 | 0.04 | 29.0 | 30.0 |

Ratios against bare — ACU: hybrid **1.13x**, acli **1.30x**. Perception tokens:
hybrid **0.74x**, acli **1.06x**. Iterations: hybrid **1.10x**, acli **1.22x**. Exec calls:
hybrid **1.18x**, acli **1.20x**. Tasks done: hybrid **0.98x**, acli **1.00x**.

Worst run by perception tokens — hybrid 47,409 (unitto|hybrid|2), bare 118,178 (joplin|bare|1), acli 105,687 (amaze|acli|1).


### ACU by stack

| stack | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 12.2 | 0.28 | 9.1 | 0.09 | 12.0 | 0.30 | 1.35x | 1.32x |
| rn | 9.1 | 0.50 | 10.3 | 0.42 | 12.7 | 0.24 | 0.88x | 1.23x |
| views | 17.6 | 0.23 | 15.0 | 0.26 | 20.0 | 0.33 | 1.18x | 1.34x |
| **all** | 13.0 | 0.40 | 11.5 | 0.36 | 14.9 | 0.38 | 1.13x | 1.30x |

### Perception tokens by stack

| stack | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 42,300 | 0.09 | 40,936 | 0.24 | 39,862 | 0.22 | 1.03x | 0.97x |
| rn | 27,569 | 0.35 | 63,112 | 0.73 | 56,944 | 0.43 | 0.44x | 0.90x |
| views | 39,545 | 0.14 | 44,517 | 0.36 | 59,976 | 0.54 | 0.89x | 1.35x |
| **all** | 36,471 | 0.25 | 49,522 | 0.56 | 52,260 | 0.45 | 0.74x | 1.06x |

### Iterations by stack

| stack | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 170 | 0.23 | 140 | 0.12 | 173 | 0.24 | 1.22x | 1.24x |
| rn | 127 | 0.43 | 135 | 0.37 | 161 | 0.18 | 0.94x | 1.19x |
| views | 221 | 0.18 | 196 | 0.21 | 243 | 0.26 | 1.12x | 1.24x |
| **all** | 173 | 0.33 | 157 | 0.29 | 192 | 0.29 | 1.10x | 1.22x |

### Screenshots by stack

| stack | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 9.2 | 0.44 | 16.2 | 0.46 | 13.8 | 0.43 | 0.57x | 0.85x |
| rn | 3.0 | 0.38 | 31.0 | 1.02 | 28.2 | 0.59 | 0.10x | 0.91x |
| views | 4.2 | 0.45 | 11.0 | 1.10 | 24.8 | 0.92 | 0.39x | 2.25x |
| **all** | 5.5 | 0.67 | 19.4 | 1.04 | 22.2 | 0.73 | 0.28x | 1.15x |

### Tasks done (of ~30) by stack

| stack | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 26.2 | 0.04 | 27.0 | 0.03 | 27.2 | 0.02 | 0.97x | 1.01x |
| rn | 28.5 | 0.05 | 29.5 | 0.02 | 28.8 | 0.04 | 0.97x | 0.97x |
| views | 28.0 | 0.03 | 28.2 | 0.02 | 28.5 | 0.02 | 0.99x | 1.01x |
| **all** | 27.6 | 0.05 | 28.2 | 0.04 | 28.2 | 0.04 | 0.98x | 1.00x |

### ACU by app

| app | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| amaze | 21.0 | 0.01 | 18.4 | 0.06 | 25.7 | 0.04 | 1.14x | 1.40x |
| joplin | 13.0 | 0.13 | 13.9 | 0.00 | 14.9 | 0.06 | 0.93x | 1.07x |
| lesspass | 5.3 | 0.11 | 6.7 | 0.32 | 10.6 | 0.28 | 0.79x | 1.57x |
| markor | 14.2 | 0.10 | 11.6 | 0.03 | 14.3 | 0.03 | 1.23x | 1.23x |
| seal | 14.5 | 0.24 | 9.8 | 0.01 | 14.6 | 0.23 | 1.48x | 1.49x |
| unitto | 10.0 | 0.17 | 8.3 | 0.01 | 9.3 | 0.07 | 1.20x | 1.12x |
| **all** | 13.0 | 0.40 | 11.5 | 0.36 | 14.9 | 0.38 | 1.13x | 1.30x |

### Perception tokens by app

| app | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| amaze | 44,128 | 0.01 | 53,160 | 0.39 | 82,882 | 0.39 | 0.83x | 1.56x |
| joplin | 35,648 | 0.08 | 100,911 | 0.24 | 77,969 | 0.02 | 0.35x | 0.77x |
| lesspass | 19,490 | 0.09 | 25,314 | 0.23 | 35,918 | 0.09 | 0.77x | 1.42x |
| markor | 34,962 | 0.10 | 35,874 | 0.16 | 37,069 | 0.15 | 0.97x | 1.03x |
| seal | 39,982 | 0.05 | 32,406 | 0.05 | 42,075 | 0.34 | 1.23x | 1.30x |
| unitto | 44,617 | 0.09 | 49,467 | 0.05 | 37,648 | 0.05 | 0.90x | 0.76x |
| **all** | 36,471 | 0.25 | 49,522 | 0.56 | 52,260 | 0.45 | 0.74x | 1.06x |

### Billed input tokens (what ACU tracks)

| | hybrid | bare | acli |
|---|---:|---:|---:|
| billed input, median | 13.37 Mtok | 10.41 Mtok | 13.65 Mtok |
| billed input, mean | 13.84 Mtok | 11.34 Mtok | 15.09 Mtok |
| peak resident context | 120,877 | 109,058 | 118,136 |
| turns | 173 | 157 | 192 |
| perception tokens | 36,471 | 49,522 | 52,260 |

Billed input is the integral of context size over turns, so a token added at turn *i* is charged again at every turn after it. Against bare on the median run: hybrid **1.28x**, acli **1.31x** — a perception ratio does not carry into cost, because a whole run's perception spend is a fraction of a percent of what it bills.

### Where the ACU goes

| per run | hybrid | bare | acli |
|---|---:|---:|---:|
| commands before the first action | 7.33 | 9.92 | 22.92 |
| of those, writing its own tooling | 0.25 | 0.75 | 0.58 |
| looks/task | 4.14 | 2.68 | 3.38 |
| perception tokens per look | 469 | 1,442 | 689 |
| actions per look | 1.73 | 4.28 | 0.87 |
| blind multi-action commands | 11.58 | 21.50 | 7.25 |
| turns/task | 6.29 | 5.59 | 6.85 |
| ACU/turn | 0.0735 | 0.0719 | 0.0761 |
| ACU/task | 0.47 | 0.41 | 0.53 |

Across the 24 hybrid/bare cells, one extra look per task costs **0.053 ACU per task** (1.48 ACU over a 28-task run) — the strongest per-cell predictor of ACU after turn count itself. hybrid takes 4.14 looks per task against bare's 2.68, which alone prices at +2.15 ACU per run against an observed gap of +1.85. The cheaper look is spent on more looking: bootstrapping the improvised tooling is 0.8 commands of a 157-turn run, so there is no setup tax to amortise.

### Which observation verb the hybrid arm typed

| verb | calls | share |
|---|---:|---:|
| `hd see --find` | 741 | 57% |
| `hd see (delta on a re-observation)` | 495 | 38% |
| `hd see --full` | 44 | 3% |
| `hd see -q (capture, print nothing)` | 12 | 1% |

Of the 495 plain `hd see` re-observations, 242 (49%) directly followed a `--find`/`--full`/`-q`. Those render the full tree, so a baseline keyed off the verb leaves a compact `see` nothing of its own kind to diff against and it prints the whole tree — silently, without even the "screen changed too much" line.

### Did the acli arm use accessibility-cli?

12/12 acli runs invoked the binary. 496 of 1,052 invocations went through a shell wrapper the agent defined (`A --llm-query`), not the literal name.

| invocation | calls | share |
|---|---:|---:|
| `accessibility-cli action (tap/type/key/adb-*)` | 628 | 60% |
| `accessibility-cli other` | 248 | 24% |
| `accessibility-cli --llm (whole tree)` | 167 | 16% |
| `accessibility-cli screenshot / annotate` | 5 | 0% |
| `accessibility-cli -q (CSS-like query)` | 4 | 0% |

## Method notes

- Perception tokens come from each session's final `context_growth_update` event
  (`approx_ant_tokens` per tool, plus image tokens for screenshots) — measured, not estimated
  from transcripts, and identical bookkeeping for every arm.
- Spread is the coefficient of variation: the arms differ in scale, so an absolute SD would
  flatter whichever arm is cheaper.
- Some suites cap below 30/30 in EVERY arm because the remaining tasks need an account or a
  network service (Jerboa needs a Lemmy login). That is the suite's ceiling, not an arm failing.
- Raw data: `runs.json` (cell -> session), `metrics.json`, `tasks.json`, `bypass.json`.

