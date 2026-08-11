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
12 screenshots across ~30 tasks. So this mostly measures **the skill vs. visual computer use**, the comparison the plugin README claims — and it is the flattering framing, not the harsh one. Re-check
this split every run before quoting the numbers; it decides which experiment you ran, and it
has flipped between runs of the same matrix.

The opposite failure — completing tasks by writing device state instead of driving the UI
(`adb shell mkdir` for "create a folder") — is counted too: runs touching device state directly,
7/12 hybrid, 7/12 bare, 4/12 acli.
A large imbalance here invalidates the ACU comparison, because one arm is doing less work.

## Headline

| metric | arm | mean | median | cv | p90 | max |
|---|---|---|---|---|---|---|
| ACU | hybrid | 14.6 | 14.1 | 0.44 | 17.8 | 27.0 |
| ACU | bare | 13.3 | 12.6 | 0.46 | 17.5 | 25.2 |
| ACU | acli | 15.6 | 14.5 | 0.30 | 19.2 | 25.2 |
| perception tokens | hybrid | 36,845 | 36,159 | 0.32 | 45,781 | 57,366 |
| perception tokens | bare | 55,212 | 39,452 | 0.89 | 69,757 | 201,749 |
| perception tokens | acli | 49,194 | 47,589 | 0.22 | 58,441 | 65,869 |
| screenshots | hybrid | 6 | 4 | 0.55 | 8 | 13 |
| screenshots | bare | 23 | 12 | 1.39 | 24 | 120 |
| screenshots | acli | 15 | 16 | 0.49 | 20 | 29 |
| tasks done (of ~30) | hybrid | 28.2 | 28.0 | 0.04 | 29.0 | 30.0 |
| tasks done (of ~30) | bare | 27.9 | 28.0 | 0.04 | 29.0 | 30.0 |
| tasks done (of ~30) | acli | 28.1 | 28.5 | 0.06 | 29.0 | 30.0 |

Ratios against bare — ACU: hybrid **1.10x**, acli **1.18x**. Perception tokens:
hybrid **0.67x**, acli **0.89x**. Iterations: hybrid **1.13x**, acli **1.21x**. Exec calls:
hybrid **1.29x**, acli **1.29x**. Tasks done: hybrid **1.01x**, acli **1.01x**.

Worst run by perception tokens — hybrid 57,366 (amaze|hybrid|1), bare 201,749 (joplin|bare|2), acli 65,869 (unitto|acli|1).


### ACU by stack

| stack | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 14.3 | 0.24 | 10.8 | 0.32 | 14.2 | 0.06 | 1.32x | 1.31x |
| rn | 8.9 | 0.35 | 10.5 | 0.54 | 12.0 | 0.17 | 0.85x | 1.14x |
| views | 20.7 | 0.30 | 18.4 | 0.35 | 20.6 | 0.22 | 1.12x | 1.12x |
| **all** | 14.6 | 0.44 | 13.3 | 0.46 | 15.6 | 0.30 | 1.10x | 1.18x |

### Perception tokens by stack

| stack | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 40,135 | 0.13 | 38,229 | 0.34 | 50,688 | 0.22 | 1.05x | 1.33x |
| rn | 24,672 | 0.32 | 78,882 | 1.08 | 48,703 | 0.33 | 0.31x | 0.62x |
| views | 45,728 | 0.23 | 48,525 | 0.34 | 48,191 | 0.11 | 0.94x | 0.99x |
| **all** | 36,845 | 0.32 | 55,212 | 0.89 | 49,194 | 0.22 | 0.67x | 0.89x |

### Iterations by stack

| stack | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 185 | 0.23 | 150 | 0.23 | 183 | 0.08 | 1.23x | 1.22x |
| rn | 125 | 0.37 | 120 | 0.37 | 147 | 0.14 | 1.04x | 1.23x |
| views | 229 | 0.23 | 204 | 0.26 | 243 | 0.20 | 1.12x | 1.19x |
| **all** | 180 | 0.35 | 158 | 0.34 | 191 | 0.26 | 1.13x | 1.21x |

### Screenshots by stack

| stack | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 9 | 0.30 | 15 | 0.58 | 15 | 0.52 | 0.61x | 1.00x |
| rn | 3 | 0.27 | 39 | 1.40 | 17 | 0.60 | 0.08x | 0.43x |
| views | 6 | 0.43 | 14 | 0.61 | 15 | 0.45 | 0.39x | 1.04x |
| **all** | 6 | 0.55 | 23 | 1.39 | 15 | 0.49 | 0.26x | 0.68x |

### Tasks done (of ~30) by stack

| stack | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 27.0 | 0.05 | 26.8 | 0.04 | 27.0 | 0.07 | 1.01x | 1.01x |
| rn | 29.2 | 0.02 | 28.8 | 0.04 | 28.8 | 0.04 | 1.02x | 1.00x |
| views | 28.2 | 0.02 | 28.2 | 0.02 | 28.5 | 0.05 | 1.00x | 1.01x |
| **all** | 28.2 | 0.04 | 27.9 | 0.04 | 28.1 | 0.06 | 1.01x | 1.01x |

### ACU by app

| app | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| amaze | 26.1 | 0.05 | 23.9 | 0.07 | 24.3 | 0.05 | 1.09x | 1.01x |
| joplin | 10.7 | 0.34 | 15.1 | 0.22 | 13.7 | 0.05 | 0.71x | 0.91x |
| lesspass | 7.1 | 0.24 | 5.9 | 0.06 | 10.3 | 0.01 | 1.20x | 1.74x |
| markor | 15.3 | 0.04 | 13.0 | 0.05 | 17.0 | 0.18 | 1.18x | 1.31x |
| seal | 17.2 | 0.05 | 13.5 | 0.20 | 14.8 | 0.02 | 1.27x | 1.09x |
| unitto | 11.4 | 0.03 | 8.2 | 0.04 | 13.7 | 0.07 | 1.40x | 1.67x |
| **all** | 14.6 | 0.44 | 13.3 | 0.46 | 15.6 | 0.30 | 1.10x | 1.18x |

### Perception tokens by app

| app | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| amaze | 54,088 | 0.09 | 57,374 | 0.39 | 51,658 | 0.09 | 0.94x | 0.90x |
| joplin | 30,938 | 0.16 | 135,753 | 0.69 | 61,767 | 0.08 | 0.23x | 0.45x |
| lesspass | 18,408 | 0.06 | 22,010 | 0.00 | 35,640 | 0.27 | 0.84x | 1.62x |
| markor | 37,368 | 0.17 | 39,676 | 0.09 | 44,724 | 0.06 | 0.94x | 1.13x |
| seal | 44,277 | 0.05 | 46,704 | 0.31 | 42,742 | 0.10 | 0.95x | 0.92x |
| unitto | 35,992 | 0.08 | 29,754 | 0.16 | 58,633 | 0.17 | 1.21x | 1.97x |
| **all** | 36,845 | 0.32 | 55,212 | 0.89 | 49,194 | 0.22 | 0.67x | 0.89x |

### Billed input tokens (what ACU tracks)

| | hybrid | bare | acli |
|---|---:|---:|---:|
| billed input, median | 14.68 Mtok | 12.24 Mtok | 15.04 Mtok |
| billed input, mean | 15.39 Mtok | 13.17 Mtok | 16.15 Mtok |
| peak resident context | 127,382 | 121,745 | 131,134 |
| turns | 180 | 158 | 191 |
| perception tokens | 36,845 | 55,212 | 49,194 |

Billed input is the integral of context size over turns, so a token added at turn *i* is charged again at every turn after it. Against bare on the median run: hybrid **1.20x**, acli **1.23x** — a perception ratio does not carry into cost, because a whole run's perception spend is a fraction of a percent of what it bills.

### Where the ACU goes

| per run | hybrid | bare | acli |
|---|---:|---:|---:|
| commands before the first action | 4.67 | 8.75 | 33.25 |
| of those, writing its own tooling | 0.00 | 0.50 | 0.67 |
| looks/task | 3.26 | 1.96 | 2.61 |
| perception tokens per look | 442 | 24,405 | 847 |
| actions per look | 2.02 | 8.74 | 0.69 |
| blind multi-action commands | 22.00 | 16.08 | 5.00 |
| turns/task | 6.43 | 5.69 | 6.84 |
| ACU/turn | 0.0795 | 0.0810 | 0.0813 |
| ACU/task | 0.52 | 0.48 | 0.56 |

Across the 24 hybrid/bare cells, one extra look per task costs **0.078 ACU per task** (2.19 ACU over a 28-task run) — the strongest per-cell predictor of ACU after turn count itself. hybrid takes 3.26 looks per task against bare's 1.96, which alone prices at +2.86 ACU per run against an observed gap of +1.35. The cheaper look is spent on more looking: bootstrapping the improvised tooling is 0.5 commands of a 158-turn run, so there is no setup tax to amortise.

### Which observation verb the hybrid arm typed

| verb | calls | share |
|---|---:|---:|
| `hd see --find` | 598 | 58% |
| `hd see (delta on a re-observation)` | 370 | 36% |
| `hd see --full` | 49 | 5% |
| `hd see -q (capture, print nothing)` | 6 | 1% |

Of the 370 plain `hd see` re-observations, 182 (49%) directly followed a `--find` or `-q` and 9 a `--full`. `--find` and `-q` render the whole tree but print only the matches (or nothing), so recording their tree as the diff baseline makes that next `see` compare the screen against a tree the agent never read, and answer `# no change since the last see` about a screen it has not been shown. See `evals/test_seen_baseline.py`.

### Did the acli arm use accessibility-cli?

12/12 acli runs invoked the binary. 188 of 454 invocations went through a shell wrapper the agent defined (`A --llm-query`), not the literal name.

| invocation | calls | share |
|---|---:|---:|
| `accessibility-cli action (tap/type/key/adb-*)` | 216 | 48% |
| `accessibility-cli other` | 153 | 34% |
| `accessibility-cli --llm (whole tree)` | 84 | 19% |
| `accessibility-cli -q (CSS-like query)` | 1 | 0% |

## Method notes

- Perception tokens come from each session's final `context_growth_update` event
  (`approx_ant_tokens` per tool, plus image tokens for screenshots) — measured, not estimated
  from transcripts, and identical bookkeeping for every arm.
- Spread is the coefficient of variation: the arms differ in scale, so an absolute SD would
  flatter whichever arm is cheaper.
- Some suites cap below 30/30 in EVERY arm because the remaining tasks need an account or a
  network service (Jerboa needs a Lemmy login). That is the suite's ceiling, not an arm failing.
- Command-derived sections (verbs, adoption, looks/task) read `shell_process_started` events,
  which cover 96% hybrid, 91% bare, 81% acli of each arm's `exec` calls: a command run inside a shell script or a
  loop the agent wrote is one event, so counts are a floor, and they are a lower floor for the
  arm that wrapped its tool.
- Raw data: `runs.json` (cell -> session), `metrics.json`, `tasks.json`, `bypass.json`.

