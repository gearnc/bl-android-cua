# android-hybrid-navigation vs. unguided agent vs. accessibility-cli — 36-run blinded eval

**Matrix.** 6 apps x 3 arms x 2 replicates = 36 child sessions,
Normal capability, ~30 machine-verifiable tasks per app, one app per session. Apps:
amaze, joplin, lesspass, markor, seal, unitto. Arms: hybrid, bare, acli. Every run booted the same emulator snapshot
(Android 14, API 34, 720x1280 @320dpi, F-Droid APKs preinstalled) and ended with a fixed `adb`
state dump, so grading is not self-report. Arms were blind and differ by exactly one paragraph:
hybrid was told only to use whatever tooling it has, bare was forbidden the skill, acli was forbidden the skill and pointed at the prebuilt `accessibility-cli` binary. Ratios are against **bare**.

## What the bare arm actually does

**Mostly it is not screenshot-driven CUA.** Denied the skill, agents sometimes reinvent it — a bare session may write a
`uiautomator dump` wrapper (`ui.sh`, `t.sh`, `ui.py`) in its first minute and grep it — and
sometimes just looks at the screen. Counting a run as *improvised tree tooling* at
<= 5 screenshots and as *visual CUA* at >= 20: 7/12 bare runs
improvised tree tooling, 1/12 did visual CUA,
4 sat in between. Median bare run:
4 screenshots across ~30 tasks. So this mostly measures **the skill vs. agent-improvised tree tooling**, not the skill vs. looking at the screen — a harsher bar than the README's. Re-check
this split every run before quoting the numbers; it decides which experiment you ran, and it
has flipped between runs of the same matrix.

The opposite failure — completing tasks by writing device state instead of driving the UI
(`adb shell mkdir` for "create a folder") — is counted too: runs touching device state directly,
3/12 hybrid, 1/12 bare, 2/12 acli.
A large imbalance here invalidates the ACU comparison, because one arm is doing less work.

## Headline

| metric | arm | mean | median | cv | p90 | max |
|---|---|---|---|---|---|---|
| ACU | hybrid | 13.0 | 12.6 | 0.40 | 17.0 | 21.2 |
| ACU | bare | 11.5 | 10.6 | 0.36 | 14.0 | 19.1 |
| ACU | acli | 14.9 | 14.1 | 0.38 | 16.9 | 26.5 |
| perception tokens | hybrid | 19,500 | 15,868 | 0.62 | 22,080 | 44,295 |
| perception tokens | bare | 20,612 | 18,094 | 0.60 | 22,288 | 51,731 |
| perception tokens | acli | 29,918 | 17,847 | 0.96 | 52,337 | 105,687 |
| screenshots | hybrid | 2.9 | 2.0 | 0.97 | 5.0 | 9.0 |
| screenshots | bare | 8.1 | 4.5 | 1.17 | 11.0 | 33.0 |
| screenshots | acli | 11.9 | 6.0 | 1.34 | 20.0 | 58.0 |
| tasks done (of ~30) | hybrid | 27.6 | 27.5 | 0.05 | 29.0 | 30.0 |
| tasks done (of ~30) | bare | 28.2 | 28.0 | 0.04 | 29.0 | 30.0 |
| tasks done (of ~30) | acli | 28.2 | 28.0 | 0.04 | 29.0 | 30.0 |

Ratios against bare — ACU: hybrid **1.13x**, acli **1.30x**. Perception tokens:
hybrid **0.95x**, acli **1.45x**. Iterations: hybrid **1.45x**, acli **1.74x**. Exec calls:
hybrid **1.57x**, acli **1.76x**. Tasks done: hybrid **0.98x**, acli **1.00x**.

Worst run by perception tokens — hybrid 44,295 (amaze|hybrid|2), bare 51,731 (joplin|bare|1), acli 105,687 (amaze|acli|1).


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
| compose | 15,699 | 0.32 | 16,635 | 0.36 | 24,246 | 0.79 | 0.94x | 1.46x |
| rn | 15,520 | 0.13 | 31,472 | 0.52 | 17,344 | 0.17 | 0.49x | 0.55x |
| views | 27,279 | 0.71 | 13,728 | 0.34 | 48,163 | 0.92 | 1.99x | 3.51x |
| **all** | 19,500 | 0.62 | 20,612 | 0.60 | 29,918 | 0.96 | 0.95x | 1.45x |

### Iterations by stack

| stack | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 58 | 0.09 | 56 | 0.10 | 97 | 0.85 | 1.04x | 1.73x |
| rn | 64 | 0.09 | 70 | 0.11 | 58 | 0.10 | 0.91x | 0.83x |
| views | 158 | 0.70 | 68 | 0.03 | 182 | 0.73 | 2.34x | 2.69x |
| **all** | 94 | 0.81 | 65 | 0.13 | 112 | 0.87 | 1.45x | 1.74x |

### Screenshots by stack

| stack | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 3.5 | 1.25 | 6.8 | 0.64 | 8.5 | 1.11 | 0.52x | 1.26x |
| rn | 2.0 | 0.71 | 15.2 | 0.90 | 6.0 | 0.41 | 0.13x | 0.39x |
| views | 3.2 | 0.81 | 2.2 | 1.17 | 21.2 | 1.21 | 1.44x | 9.44x |
| **all** | 2.9 | 0.97 | 8.1 | 1.17 | 11.9 | 1.34 | 0.36x | 1.47x |

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
| amaze | 44,128 | 0.01 | 15,518 | 0.40 | 82,882 | 0.39 | 2.84x | 5.34x |
| joplin | 15,174 | 0.22 | 44,477 | 0.23 | 17,062 | 0.20 | 0.34x | 0.38x |
| lesspass | 15,868 | 0.06 | 18,466 | 0.16 | 17,628 | 0.20 | 0.86x | 0.95x |
| markor | 10,430 | 0.07 | 11,938 | 0.30 | 13,444 | 0.03 | 0.87x | 1.13x |
| seal | 11,714 | 0.06 | 11,419 | 0.02 | 30,644 | 1.00 | 1.03x | 2.68x |
| unitto | 19,684 | 0.17 | 21,851 | 0.03 | 17,847 | 0.04 | 0.90x | 0.82x |
| **all** | 19,500 | 0.62 | 20,612 | 0.60 | 29,918 | 0.96 | 0.95x | 1.45x |

### Billed input tokens (what ACU tracks)

| | hybrid | bare | acli |
|---|---:|---:|---:|
| billed input, median | 3.19 Mtok | 3.09 Mtok | 3.09 Mtok |
| billed input, mean | 6.52 Mtok | 3.17 Mtok | 8.06 Mtok |
| peak resident context | 81,541 | 65,009 | 82,056 |
| turns | 94 | 65 | 112 |
| perception tokens | 19,500 | 20,612 | 29,918 |

Billed input is the integral of context size over turns, so a token added at turn *i* is charged again at every turn after it. Against bare on the median run: hybrid **1.03x**, acli **1.00x** — a perception ratio does not carry into cost, because a whole run's perception spend is a fraction of a percent of what it bills.

### Which observation verb the hybrid arm typed

| verb | calls | share |
|---|---:|---:|
| `hd see --find` | 214 | 51% |
| `hd see (delta on a re-observation)` | 185 | 44% |
| `hd see --full` | 14 | 3% |
| `hd see -q (capture, print nothing)` | 3 | 1% |

Of the 185 plain `hd see` re-observations, 73 (39%) directly followed a `--find`/`--full`/`-q`. Those render the full tree, so a baseline keyed off the verb leaves a compact `see` nothing of its own kind to diff against and it prints the whole tree — silently, without even the "screen changed too much" line.

### Did the acli arm use accessibility-cli?

12/12 acli runs invoked the binary. 117 of 340 invocations went through a shell wrapper the agent defined (`A --llm-query`), not the literal name.

| invocation | calls | share |
|---|---:|---:|
| `accessibility-cli action (tap/type/key/adb-*)` | 177 | 52% |
| `accessibility-cli other` | 105 | 31% |
| `accessibility-cli --llm (whole tree)` | 57 | 17% |
| `accessibility-cli -q (CSS-like query)` | 1 | 0% |

## Method notes

- Perception tokens come from each session's final `context_growth_update` event
  (`approx_ant_tokens` per tool, plus image tokens for screenshots) — measured, not estimated
  from transcripts, and identical bookkeeping for every arm.
- Spread is the coefficient of variation: the arms differ in scale, so an absolute SD would
  flatter whichever arm is cheaper.
- Some suites cap below 30/30 in EVERY arm because the remaining tasks need an account or a
  network service (Jerboa needs a Lemmy login). That is the suite's ceiling, not an arm failing.
- Raw data: `runs.json` (cell -> session), `metrics.json`, `tasks.json`, `bypass.json`.

