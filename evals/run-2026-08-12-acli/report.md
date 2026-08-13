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
<= 5 screenshots and as *visual CUA* at >= 20: 2/12 bare runs
improvised tree tooling, 4/12 did visual CUA,
6 sat in between. Median bare run:
12 screenshots across ~30 tasks. So this mostly measures **the skill vs. visual computer use**, the comparison the plugin README claims — and it is the flattering framing, not the harsh one. Re-check
this split every run before quoting the numbers; it decides which experiment you ran, and it
has flipped between runs of the same matrix.

The opposite failure — completing tasks by writing device state instead of driving the UI
(`adb shell mkdir` for "create a folder") — is counted too: runs touching device state directly,
4/12 hybrid, 6/12 bare, 4/12 acli.
A large imbalance here invalidates the ACU comparison, because one arm is doing less work.

## Headline

| metric | arm | mean | median | cv | p90 | max |
|---|---|---|---|---|---|---|
| ACU | hybrid | 12.1 | 13.3 | 0.35 | 14.9 | 18.7 |
| ACU | bare | 12.4 | 11.9 | 0.38 | 16.7 | 20.0 |
| ACU | acli | 14.1 | 12.8 | 0.34 | 15.8 | 25.4 |
| perception tokens | hybrid | 37,596 | 40,387 | 0.34 | 44,026 | 59,267 |
| perception tokens | bare | 49,299 | 49,085 | 0.41 | 62,831 | 93,206 |
| perception tokens | acli | 44,033 | 40,382 | 0.37 | 61,309 | 74,029 |
| screenshots | hybrid | 4.8 | 3.5 | 0.63 | 8.0 | 10.0 |
| screenshots | bare | 17.0 | 11.5 | 0.82 | 25.0 | 50.0 |
| screenshots | acli | 15.6 | 10.0 | 0.86 | 34.0 | 38.0 |
| tasks done (of ~30) | hybrid | 28.3 | 28.0 | 0.04 | 29.0 | 30.0 |
| tasks done (of ~30) | bare | 27.7 | 28.0 | 0.04 | 28.0 | 29.0 |
| tasks done (of ~30) | acli | 27.9 | 28.0 | 0.04 | 28.0 | 30.0 |

Ratios against bare — ACU: hybrid **0.97x**, acli **1.14x**. Perception tokens:
hybrid **0.76x**, acli **0.89x**. Iterations: hybrid **0.98x**, acli **1.15x**. Exec calls:
hybrid **1.10x**, acli **1.20x**. Tasks done: hybrid **1.02x**, acli **1.01x**.

Worst run by perception tokens — hybrid 59,267 (seal|hybrid|2), bare 93,206 (seal|bare|1), acli 74,029 (joplin|acli|2).


### ACU by stack

| stack | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 12.3 | 0.27 | 12.9 | 0.22 | 11.8 | 0.09 | 0.95x | 0.91x |
| rn | 8.1 | 0.45 | 7.7 | 0.39 | 12.0 | 0.31 | 1.05x | 1.55x |
| views | 15.8 | 0.12 | 16.5 | 0.20 | 18.4 | 0.30 | 0.96x | 1.12x |
| **all** | 12.1 | 0.35 | 12.4 | 0.38 | 14.1 | 0.34 | 0.97x | 1.14x |

### Perception tokens by stack

| stack | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 46,324 | 0.19 | 64,265 | 0.34 | 39,050 | 0.09 | 0.72x | 0.61x |
| rn | 25,899 | 0.56 | 33,966 | 0.52 | 56,685 | 0.37 | 0.76x | 1.67x |
| views | 40,566 | 0.09 | 49,666 | 0.21 | 36,363 | 0.37 | 0.82x | 0.73x |
| **all** | 37,596 | 0.34 | 49,299 | 0.41 | 44,033 | 0.37 | 0.76x | 0.89x |

### Iterations by stack

| stack | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 160 | 0.26 | 171 | 0.14 | 160 | 0.08 | 0.94x | 0.93x |
| rn | 110 | 0.34 | 109 | 0.32 | 154 | 0.21 | 1.01x | 1.41x |
| views | 190 | 0.13 | 190 | 0.22 | 228 | 0.27 | 1.00x | 1.20x |
| **all** | 154 | 0.30 | 157 | 0.30 | 181 | 0.28 | 0.98x | 1.15x |

### Screenshots by stack

| stack | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 8.0 | 0.18 | 29.2 | 0.58 | 8.8 | 0.25 | 0.27x | 0.30x |
| rn | 3.2 | 1.05 | 11.2 | 0.79 | 29.8 | 0.40 | 0.29x | 2.64x |
| views | 3.2 | 0.15 | 10.5 | 0.60 | 8.2 | 1.31 | 0.31x | 0.79x |
| **all** | 4.8 | 0.63 | 17.0 | 0.82 | 15.6 | 0.86 | 0.28x | 0.92x |

### Tasks done (of ~30) by stack

| stack | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 27.5 | 0.05 | 27.0 | 0.04 | 27.2 | 0.04 | 1.02x | 1.01x |
| rn | 28.8 | 0.03 | 28.0 | 0.03 | 28.8 | 0.03 | 1.03x | 1.03x |
| views | 28.8 | 0.03 | 28.0 | 0.03 | 27.8 | 0.02 | 1.03x | 0.99x |
| **all** | 28.3 | 0.04 | 27.7 | 0.04 | 27.9 | 0.04 | 1.02x | 1.01x |

### ACU by app

| app | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| amaze | 16.8 | 0.16 | 18.0 | 0.15 | 22.6 | 0.17 | 0.93x | 1.25x |
| joplin | 11.0 | 0.14 | 10.1 | 0.20 | 15.1 | 0.00 | 1.10x | 1.50x |
| lesspass | 5.2 | 0.31 | 5.3 | 0.02 | 8.8 | 0.15 | 0.97x | 1.66x |
| markor | 14.8 | 0.03 | 14.9 | 0.27 | 14.3 | 0.15 | 0.99x | 0.96x |
| seal | 14.8 | 0.00 | 14.3 | 0.24 | 12.5 | 0.04 | 1.04x | 0.88x |
| unitto | 9.8 | 0.27 | 11.6 | 0.18 | 11.1 | 0.09 | 0.84x | 0.96x |
| **all** | 12.1 | 0.35 | 12.4 | 0.38 | 14.1 | 0.34 | 0.97x | 1.14x |

### Perception tokens by app

| app | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| amaze | 41,589 | 0.12 | 56,534 | 0.16 | 46,594 | 0.18 | 0.74x | 0.82x |
| joplin | 37,721 | 0.22 | 46,467 | 0.38 | 69,672 | 0.09 | 0.81x | 1.50x |
| lesspass | 14,078 | 0.24 | 21,464 | 0.08 | 43,698 | 0.57 | 0.66x | 2.04x |
| markor | 39,544 | 0.08 | 42,800 | 0.17 | 26,132 | 0.26 | 0.92x | 0.61x |
| seal | 51,646 | 0.21 | 66,697 | 0.56 | 39,292 | 0.15 | 0.77x | 0.59x |
| unitto | 41,002 | 0.07 | 61,833 | 0.06 | 38,810 | 0.05 | 0.66x | 0.63x |
| **all** | 37,596 | 0.34 | 49,299 | 0.41 | 44,033 | 0.37 | 0.76x | 0.89x |

### Billed input tokens (what ACU tracks)

| | hybrid | bare | acli |
|---|---:|---:|---:|
| billed input, median | 13.74 Mtok | 11.95 Mtok | 13.09 Mtok |
| billed input, mean | 12.68 Mtok | 12.51 Mtok | 14.18 Mtok |
| peak resident context | 124,690 | 120,662 | 119,115 |
| turns | 154 | 157 | 181 |
| perception tokens | 37,596 | 49,299 | 44,033 |

Billed input is the integral of context size over turns, so a token added at turn *i* is charged again at every turn after it. Against bare on the median run: hybrid **1.15x**, acli **1.10x** — a perception ratio does not carry into cost, because a whole run's perception spend is a fraction of a percent of what it bills.

### Where the ACU goes

| per run | hybrid | bare | acli |
|---|---:|---:|---:|
| commands before the first action | 5.58 | 9.92 | 13.83 |
| of those, writing its own tooling | 0.08 | 0.92 | 0.33 |
| looks/task | 3.34 | 2.63 | 2.92 |
| perception tokens per look | 474 | 1,169 | 839 |
| actions per look | 2.16 | 2.08 | 0.64 |
| blind multi-action commands | 18.58 | 12.25 | 4.00 |
| turns/task | 5.45 | 5.67 | 6.49 |
| ACU/turn | 0.0769 | 0.0771 | 0.0768 |
| ACU/task | 0.43 | 0.45 | 0.50 |

Across the 24 hybrid/bare cells, one extra look per task costs **0.050 ACU per task** (1.39 ACU over a 28-task run) — the strongest per-cell predictor of ACU after turn count itself. hybrid takes 3.34 looks per task against bare's 2.63, which alone prices at +0.98 ACU per run against an observed gap of -0.56. The cheaper look is spent on more looking: bootstrapping the improvised tooling is 0.9 commands of a 157-turn run, so there is no setup tax to amortise.

### Which observation verb the hybrid arm typed

| verb | calls | share |
|---|---:|---:|
| `hd see --find` | 621 | 59% |
| `hd see (delta on a re-observation)` | 420 | 40% |
| `hd see --full` | 20 | 2% |

Of the 420 plain `hd see` re-observations, 195 (46%) directly followed a `--find` or `-q` and 5 a `--full`. `--find` and `-q` render the whole tree but print only the matches (or nothing), so this revision keys the diff baseline off the rendering the caller was SHOWN: those re-observations diff against the last tree that actually reached the agent rather than answering `# no change since the last see` about a screen it has never seen. `evals/test_seen_baseline.py` is the regression; re-read this share every run, since it decides how much that behaviour is worth.

### Replacing a value that is already in a field

| | hybrid | bare | acli |
|---|---:|---:|---:|
| hand-rolled deletion loops | 28 | 12 | 9 |
| runs doing it | 8/12 | 4/12 | 3/12 |

Every arm meets the same fields, and none of the three tools had a verb for emptying one, so the agents sent `KEYCODE_MOVE_END` and a guessed number of backspaces. The count is not knowable from outside the tree — the guesses escalate within a run (`seal|hybrid|1`: 20, 30, 10, 30, 30, 40, 20, 40, 20) and a low one leaves the tail of the old value fused to the new text. `hd type "x" -r` takes the count from the focused node's own text; `evals/test_replace.py` prices it against the guess.

### Did the acli arm use accessibility-cli?

12/12 acli runs invoked the binary. 303 of 844 invocations went through a shell wrapper the agent defined (`A --llm-query`), not the literal name.

| invocation | calls | share |
|---|---:|---:|
| `accessibility-cli action (tap/type/key/adb-*)` | 467 | 55% |
| `accessibility-cli other` | 278 | 33% |
| `accessibility-cli --llm (whole tree)` | 98 | 12% |
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
  which cover 97% hybrid, 90% bare, 84% acli of each arm's `exec` calls: a command run inside a shell script or a
  loop the agent wrote is one event, so counts are a floor, and they are a lower floor for the
  arm that wrapped its tool.
- Raw data: `runs.json` (cell -> session), `metrics.json`, `tasks.json`, `bypass.json`.

