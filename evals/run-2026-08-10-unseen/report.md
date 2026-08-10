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
<= 5 screenshots and as *visual CUA* at >= 20: 3/12 bare runs
improvised tree tooling, 2/12 did visual CUA,
7 sat in between. Median bare run:
12 screenshots across ~30 tasks. So this mostly measures **the skill vs. agent-improvised tree tooling**, not the skill vs. looking at the screen — a harsher bar than the README's. Re-check
this split every run before quoting the numbers; it decides which experiment you ran, and it
has flipped between runs of the same matrix.

The opposite failure — completing tasks by writing device state instead of driving the UI
(`adb shell mkdir` for "create a folder") — is counted too: runs touching device state directly,
6/12 hybrid, 5/12 bare, 4/12 acli.
A large imbalance here invalidates the ACU comparison, because one arm is doing less work.

## Headline

| metric | arm | mean | median | cv | p90 | max |
|---|---|---|---|---|---|---|
| ACU | hybrid | 14.1 | 15.2 | 0.35 | 17.4 | 24.4 |
| ACU | bare | 10.8 | 10.6 | 0.35 | 13.7 | 19.6 |
| ACU | acli | 14.3 | 13.6 | 0.29 | 19.4 | 22.2 |
| perception tokens | hybrid | 38,526 | 43,754 | 0.31 | 45,854 | 54,552 |
| perception tokens | bare | 39,968 | 37,044 | 0.31 | 50,607 | 61,931 |
| perception tokens | acli | 49,745 | 41,872 | 0.51 | 58,275 | 118,509 |
| screenshots | hybrid | 8.7 | 8.5 | 0.51 | 13.0 | 17.0 |
| screenshots | bare | 12.3 | 12.5 | 0.61 | 18.0 | 26.0 |
| screenshots | acli | 16.4 | 7.5 | 1.16 | 21.0 | 66.0 |
| tasks done (of ~30) | hybrid | 27.8 | 28.0 | 0.08 | 29.0 | 30.0 |
| tasks done (of ~30) | bare | 28.2 | 28.0 | 0.04 | 29.0 | 30.0 |
| tasks done (of ~30) | acli | 27.9 | 28.5 | 0.06 | 29.0 | 30.0 |

Ratios against bare — ACU: hybrid **1.30x**, acli **1.32x**. Perception tokens:
hybrid **0.96x**, acli **1.24x**. Iterations: hybrid **1.27x**, acli **1.25x**. Exec calls:
hybrid **1.32x**, acli **1.24x**. Tasks done: hybrid **0.99x**, acli **0.99x**.

Worst run by perception tokens — hybrid 54,552 (amaze|hybrid|2), bare 61,931 (unitto|bare|2), acli 118,509 (lesspass|acli|1).


### ACU by stack

| stack | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 13.0 | 0.20 | 10.4 | 0.07 | 14.0 | 0.40 | 1.25x | 1.35x |
| rn | 10.4 | 0.41 | 8.5 | 0.46 | 13.8 | 0.35 | 1.23x | 1.64x |
| views | 18.8 | 0.20 | 13.7 | 0.31 | 15.2 | 0.18 | 1.37x | 1.11x |
| **all** | 14.1 | 0.35 | 10.8 | 0.35 | 14.3 | 0.29 | 1.30x | 1.32x |

### Perception tokens by stack

| stack | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 40,034 | 0.12 | 39,521 | 0.42 | 38,889 | 0.17 | 1.01x | 0.98x |
| rn | 28,074 | 0.52 | 36,821 | 0.28 | 74,798 | 0.43 | 0.76x | 2.03x |
| views | 47,472 | 0.10 | 43,561 | 0.28 | 35,549 | 0.13 | 1.09x | 0.82x |
| **all** | 38,526 | 0.31 | 39,968 | 0.31 | 49,745 | 0.51 | 0.96x | 1.24x |

### Iterations by stack

| stack | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 174 | 0.20 | 145 | 0.05 | 182 | 0.35 | 1.20x | 1.25x |
| rn | 140 | 0.41 | 112 | 0.42 | 162 | 0.22 | 1.25x | 1.44x |
| views | 231 | 0.17 | 172 | 0.25 | 190 | 0.14 | 1.34x | 1.11x |
| **all** | 182 | 0.31 | 143 | 0.30 | 178 | 0.24 | 1.27x | 1.25x |

### Screenshots by stack

| stack | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 9.8 | 0.41 | 12.8 | 0.85 | 7.8 | 0.50 | 0.76x | 0.61x |
| rn | 6.5 | 0.68 | 13.5 | 0.33 | 36.0 | 0.64 | 0.48x | 2.67x |
| views | 9.8 | 0.53 | 10.8 | 0.75 | 5.5 | 0.23 | 0.91x | 0.51x |
| **all** | 8.7 | 0.51 | 12.3 | 0.61 | 16.4 | 1.16 | 0.70x | 1.33x |

### Tasks done (of ~30) by stack

| stack | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 25.8 | 0.13 | 27.2 | 0.04 | 26.2 | 0.06 | 0.94x | 0.96x |
| rn | 29.0 | 0.03 | 29.2 | 0.03 | 29.2 | 0.02 | 0.99x | 1.00x |
| views | 28.5 | 0.02 | 28.0 | 0.03 | 28.2 | 0.03 | 1.02x | 1.01x |
| **all** | 27.8 | 0.08 | 28.2 | 0.04 | 27.9 | 0.06 | 0.99x | 0.99x |

### ACU by app

| app | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| amaze | 21.0 | 0.23 | 16.8 | 0.24 | 16.5 | 0.25 | 1.25x | 0.98x |
| joplin | 13.8 | 0.16 | 11.3 | 0.30 | 12.4 | 0.24 | 1.22x | 1.09x |
| lesspass | 7.1 | 0.34 | 5.6 | 0.16 | 15.3 | 0.47 | 1.27x | 2.74x |
| markor | 16.6 | 0.07 | 10.6 | 0.00 | 13.9 | 0.04 | 1.56x | 1.31x |
| seal | 15.3 | 0.02 | 10.2 | 0.08 | 16.9 | 0.44 | 1.51x | 1.67x |
| unitto | 10.7 | 0.05 | 10.6 | 0.08 | 11.1 | 0.17 | 1.01x | 1.04x |
| **all** | 14.1 | 0.35 | 10.8 | 0.35 | 14.3 | 0.29 | 1.30x | 1.32x |

### Perception tokens by app

| app | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| amaze | 49,301 | 0.15 | 53,866 | 0.09 | 33,148 | 0.16 | 0.92x | 0.62x |
| joplin | 39,995 | 0.21 | 44,870 | 0.05 | 68,262 | 0.21 | 0.89x | 1.52x |
| lesspass | 16,153 | 0.07 | 28,772 | 0.24 | 81,335 | 0.65 | 0.56x | 2.83x |
| markor | 45,642 | 0.01 | 33,256 | 0.08 | 37,950 | 0.08 | 1.37x | 1.14x |
| seal | 39,256 | 0.19 | 28,778 | 0.33 | 39,548 | 0.14 | 1.36x | 1.37x |
| unitto | 40,811 | 0.09 | 50,264 | 0.33 | 38,229 | 0.27 | 0.81x | 0.76x |
| **all** | 38,526 | 0.31 | 39,968 | 0.31 | 49,745 | 0.51 | 0.96x | 1.24x |

### Billed input tokens (what ACU tracks)

| | hybrid | bare | acli |
|---|---:|---:|---:|
| billed input, median | 16.72 Mtok | 10.28 Mtok | 13.16 Mtok |
| billed input, mean | 15.15 Mtok | 10.84 Mtok | 14.42 Mtok |
| peak resident context | 126,999 | 114,641 | 123,040 |
| turns | 182 | 143 | 178 |
| perception tokens | 38,526 | 39,968 | 49,745 |

Billed input is the integral of context size over turns, so a token added at turn *i* is charged again at every turn after it. Against bare on the median run: hybrid **1.63x**, acli **1.28x** — a perception ratio does not carry into cost, because a whole run's perception spend is a fraction of a percent of what it bills.

### Where the ACU goes

| per run | hybrid | bare | acli |
|---|---:|---:|---:|
| commands before the first action | 5.58 | 11.25 | 18.50 |
| of those, writing its own tooling | 0.17 | 0.67 | 0.83 |
| looks/task | 3.66 | 2.16 | 2.25 |
| perception tokens per look | 415 | 1,446 | 1,534 |
| actions per look | 1.68 | 4.60 | 1.62 |
| blind multi-action commands | 16.67 | 19.25 | 6.25 |
| turns/task | 6.63 | 5.12 | 6.43 |
| ACU/turn | 0.0766 | 0.0752 | 0.0799 |
| ACU/task | 0.51 | 0.39 | 0.52 |

Across the 24 hybrid/bare cells, one extra look per task costs **0.067 ACU per task** (1.87 ACU over a 28-task run) — the strongest per-cell predictor of ACU after turn count itself. hybrid takes 3.66 looks per task against bare's 2.16, which alone prices at +2.81 ACU per run against an observed gap of +3.50. The cheaper look is spent on more looking: bootstrapping the improvised tooling is 0.7 commands of a 143-turn run, so there is no setup tax to amortise.

### Which observation verb the hybrid arm typed

| verb | calls | share |
|---|---:|---:|
| `hd see --find` | 627 | 62% |
| `hd see (delta on a re-observation)` | 287 | 28% |
| `hd see -q (capture, print nothing)` | 56 | 6% |
| `hd see --full` | 46 | 5% |

Of the 287 plain `hd see` re-observations, 157 (55%) directly followed a `--find` or `-q` and 7 a `--full`. `--find` and `-q` render the whole tree but print only the matches (or nothing), so recording their tree as the diff baseline makes that next `see` compare the screen against a tree the agent never read, and answer `# no change since the last see` about a screen it has not been shown. See `evals/test_seen_baseline.py`.

### Did the acli arm use accessibility-cli?

12/12 acli runs invoked the binary. 294 of 709 invocations went through a shell wrapper the agent defined (`A --llm-query`), not the literal name.

| invocation | calls | share |
|---|---:|---:|
| `accessibility-cli action (tap/type/key/adb-*)` | 479 | 68% |
| `accessibility-cli --llm (whole tree)` | 105 | 15% |
| `accessibility-cli other` | 101 | 14% |
| `accessibility-cli screenshot / annotate` | 19 | 3% |
| `accessibility-cli -q (CSS-like query)` | 5 | 1% |

## Method notes

- Perception tokens come from each session's final `context_growth_update` event
  (`approx_ant_tokens` per tool, plus image tokens for screenshots) — measured, not estimated
  from transcripts, and identical bookkeeping for every arm.
- Spread is the coefficient of variation: the arms differ in scale, so an absolute SD would
  flatter whichever arm is cheaper.
- Some suites cap below 30/30 in EVERY arm because the remaining tasks need an account or a
  network service (Jerboa needs a Lemmy login). That is the suite's ceiling, not an arm failing.
- Command-derived sections (verbs, adoption, looks/task) read `shell_process_started` events,
  which cover 96% hybrid, 90% bare, 82% acli of each arm's `exec` calls: a command run inside a shell script or a
  loop the agent wrote is one event, so counts are a floor, and they are a lower floor for the
  arm that wrapped its tool.
- Raw data: `runs.json` (cell -> session), `metrics.json`, `tasks.json`, `bypass.json`.

