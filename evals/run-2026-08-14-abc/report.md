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
improvised tree tooling, 1/12 did visual CUA,
8 sat in between. Median bare run:
10 screenshots across ~30 tasks. So this mostly measures **the skill vs. agent-improvised tree tooling**, not the skill vs. looking at the screen — a harsher bar than the README's. Re-check
this split every run before quoting the numbers; it decides which experiment you ran, and it
has flipped between runs of the same matrix.

The opposite failure — completing tasks by writing device state instead of driving the UI
(`adb shell mkdir` for "create a folder") — is counted too: runs touching device state directly,
5/12 hybrid, 5/12 bare, 5/12 acli.
A large imbalance here invalidates the ACU comparison, because one arm is doing less work.

## Headline

| metric | arm | mean | median | cv | p90 | max |
|---|---|---|---|---|---|---|
| ACU | hybrid | 13.4 | 13.3 | 0.31 | 15.8 | 21.8 |
| ACU | bare | 13.1 | 12.4 | 0.43 | 13.8 | 24.6 |
| ACU | acli | 15.5 | 15.0 | 0.31 | 17.8 | 26.2 |
| perception tokens | hybrid | 42,154 | 45,534 | 0.34 | 52,429 | 60,731 |
| perception tokens | bare | 41,258 | 39,305 | 0.45 | 51,509 | 78,076 |
| perception tokens | acli | 50,306 | 52,023 | 0.28 | 65,729 | 70,685 |
| screenshots | hybrid | 6.0 | 5.5 | 0.60 | 11.0 | 12.0 |
| screenshots | bare | 11.0 | 9.5 | 0.56 | 18.0 | 20.0 |
| screenshots | acli | 17.4 | 14.0 | 0.66 | 31.0 | 37.0 |
| tasks done (of ~30) | hybrid | 27.8 | 28.5 | 0.07 | 29.0 | 30.0 |
| tasks done (of ~30) | bare | 28.2 | 28.0 | 0.04 | 29.0 | 30.0 |
| tasks done (of ~30) | acli | 27.8 | 28.0 | 0.05 | 29.0 | 30.0 |

Ratios against bare — ACU: hybrid **1.02x**, acli **1.18x**. Perception tokens:
hybrid **1.02x**, acli **1.22x**. Iterations: hybrid **1.02x**, acli **1.14x**. Exec calls:
hybrid **1.06x**, acli **1.11x**. Tasks done: hybrid **0.99x**, acli **0.99x**.

Worst run by perception tokens — hybrid 60,731 (amaze|hybrid|1), bare 78,076 (amaze|bare|1), acli 70,685 (joplin|acli|2).


### ACU by stack

| stack | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 13.2 | 0.22 | 12.2 | 0.16 | 12.9 | 0.22 | 1.09x | 1.06x |
| rn | 9.9 | 0.31 | 8.9 | 0.37 | 13.7 | 0.28 | 1.11x | 1.55x |
| views | 17.0 | 0.21 | 18.2 | 0.37 | 19.9 | 0.23 | 0.93x | 1.09x |
| **all** | 13.4 | 0.31 | 13.1 | 0.43 | 15.5 | 0.31 | 1.02x | 1.18x |

### Perception tokens by stack

| stack | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 42,097 | 0.16 | 34,474 | 0.36 | 43,344 | 0.30 | 1.22x | 1.26x |
| rn | 32,640 | 0.61 | 32,022 | 0.42 | 60,578 | 0.25 | 1.02x | 1.89x |
| views | 51,725 | 0.13 | 57,277 | 0.36 | 46,996 | 0.23 | 0.90x | 0.82x |
| **all** | 42,154 | 0.34 | 41,258 | 0.45 | 50,306 | 0.28 | 1.02x | 1.22x |

### Iterations by stack

| stack | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 163 | 0.25 | 160 | 0.13 | 162 | 0.18 | 1.02x | 1.01x |
| rn | 126 | 0.29 | 112 | 0.35 | 157 | 0.23 | 1.13x | 1.40x |
| views | 213 | 0.22 | 221 | 0.38 | 243 | 0.26 | 0.96x | 1.10x |
| **all** | 168 | 0.31 | 165 | 0.41 | 187 | 0.31 | 1.02x | 1.14x |

### Screenshots by stack

| stack | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 6.8 | 0.53 | 10.2 | 0.56 | 9.2 | 0.36 | 0.66x | 0.90x |
| rn | 5.5 | 0.73 | 10.8 | 0.59 | 30.5 | 0.29 | 0.51x | 2.84x |
| views | 5.8 | 0.72 | 12.0 | 0.68 | 12.5 | 0.55 | 0.48x | 1.04x |
| **all** | 6.0 | 0.60 | 11.0 | 0.56 | 17.4 | 0.66 | 0.55x | 1.58x |

### Tasks done (of ~30) by stack

| stack | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 26.2 | 0.10 | 27.5 | 0.05 | 27.2 | 0.06 | 0.95x | 0.99x |
| rn | 28.5 | 0.05 | 28.5 | 0.05 | 28.5 | 0.06 | 1.00x | 1.00x |
| views | 28.8 | 0.02 | 28.5 | 0.02 | 27.8 | 0.03 | 1.01x | 0.97x |
| **all** | 27.8 | 0.07 | 28.2 | 0.04 | 27.8 | 0.05 | 0.99x | 0.99x |

### ACU by app

| app | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| amaze | 19.5 | 0.17 | 23.9 | 0.04 | 23.1 | 0.19 | 0.82x | 0.96x |
| joplin | 12.5 | 0.07 | 11.6 | 0.15 | 14.3 | 0.02 | 1.07x | 1.23x |
| lesspass | 7.3 | 0.09 | 6.1 | 0.00 | 13.2 | 0.49 | 1.19x | 2.15x |
| markor | 14.4 | 0.08 | 12.4 | 0.00 | 16.6 | 0.10 | 1.16x | 1.34x |
| seal | 15.3 | 0.05 | 12.2 | 0.19 | 14.0 | 0.22 | 1.26x | 1.15x |
| unitto | 11.1 | 0.24 | 12.2 | 0.20 | 11.7 | 0.27 | 0.92x | 0.96x |
| **all** | 13.4 | 0.31 | 13.1 | 0.43 | 15.5 | 0.31 | 1.02x | 1.18x |

### Perception tokens by app

| app | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| amaze | 56,580 | 0.10 | 74,199 | 0.07 | 52,776 | 0.02 | 0.76x | 0.71x |
| joplin | 49,753 | 0.09 | 43,687 | 0.02 | 69,222 | 0.03 | 1.14x | 1.58x |
| lesspass | 15,528 | 0.20 | 20,358 | 0.12 | 51,933 | 0.38 | 0.76x | 2.55x |
| markor | 46,870 | 0.08 | 40,356 | 0.23 | 41,214 | 0.37 | 1.16x | 1.02x |
| seal | 39,680 | 0.03 | 25,354 | 0.15 | 47,948 | 0.34 | 1.57x | 1.89x |
| unitto | 44,514 | 0.24 | 43,594 | 0.26 | 38,739 | 0.34 | 1.02x | 0.89x |
| **all** | 42,154 | 0.34 | 41,258 | 0.45 | 50,306 | 0.28 | 1.02x | 1.22x |

### Billed input tokens (what ACU tracks)

| | hybrid | bare | acli |
|---|---:|---:|---:|
| billed input, median | 12.82 Mtok | 11.61 Mtok | 13.36 Mtok |
| billed input, mean | 12.70 Mtok | 12.49 Mtok | 14.57 Mtok |
| peak resident context | 113,525 | 115,390 | 114,252 |
| turns | 168 | 165 | 187 |
| perception tokens | 42,154 | 41,258 | 50,306 |

Billed input is the integral of context size over turns, so a token added at turn *i* is charged again at every turn after it. Against bare on the median run: hybrid **1.10x**, acli **1.15x** — a perception ratio does not carry into cost, because a whole run's perception spend is a fraction of a percent of what it bills.

### Where the ACU goes

| per run | hybrid | bare | acli |
|---|---:|---:|---:|
| commands before the first action | 5.33 | 9.17 | 13.00 |
| of those, writing its own tooling | 0.17 | 0.33 | 0.25 |
| looks/task | 3.39 | 2.71 | 3.34 |
| perception tokens per look | 540 | 1,178 | 877 |
| actions per look | 2.56 | 4.32 | 0.66 |
| blind multi-action commands | 15.83 | 19.17 | 2.17 |
| turns/task | 6.07 | 5.86 | 6.74 |
| ACU/turn | 0.0797 | 0.0790 | 0.0826 |
| ACU/task | 0.48 | 0.46 | 0.56 |

Across the 24 hybrid/bare cells, one extra look per task costs **0.078 ACU per task** (2.17 ACU over a 28-task run) — the strongest per-cell predictor of ACU after turn count itself. hybrid takes 3.39 looks per task against bare's 2.71, which alone prices at +1.46 ACU per run against an observed gap of +0.55. The cheaper look is spent on more looking: bootstrapping the improvised tooling is 0.3 commands of a 165-turn run, so there is no setup tax to amortise.

### Which observation verb the hybrid arm typed

| verb | calls | share |
|---|---:|---:|
| `hd see --find` | 500 | 48% |
| `hd see (delta on a re-observation)` | 443 | 43% |
| `hd see --full` | 71 | 7% |
| `hd see -q (capture, print nothing)` | 24 | 2% |
| `hd see --no-diff (opt out of the delta)` | 1 | 0% |

Of the 443 plain `hd see` re-observations, 160 (36%) directly followed a `--find` or `-q` and 29 a `--full`. `--find` and `-q` render the whole tree but print only the matches (or nothing), so this revision keys the diff baseline off the rendering the caller was SHOWN: those re-observations diff against the last tree that actually reached the agent rather than answering `# no change since the last see` about a screen it has never seen. `evals/test_seen_baseline.py` is the regression; re-read this share every run, since it decides how much that behaviour is worth.


### Replacing a value that is already in a field

| | hybrid | bare | acli |
|---|---:|---:|---:|
| hand-rolled deletion loops | 7 | 10 | 2 |
| runs doing it | 3/12 | 6/12 | 2/12 |

Every arm meets the same fields, and none of the three tools had a verb for emptying one, so the agents sent `KEYCODE_MOVE_END` and a guessed number of backspaces. The count is not knowable from outside the tree — the guesses escalate within a run (`seal|hybrid|1`: 20, 30, 10, 30, 30, 40, 20, 40, 20) and a low one leaves the tail of the old value fused to the new text. `hd type "x" -r` takes the count from the focused node's own text; `evals/test_replace.py` prices it against the guess.

### Finding the focused field

| | hybrid | bare | acli |
|---|---:|---:|---:|
| focus-hunting commands | 60 | 41 | 10 |
| runs doing it | 8/12 | 10/12 | 4/12 |

The hybrid arm spent 60 commands in 8/12 runs answering a question its own tree already knew the answer to: `hd see --full | grep -i edit`, `hd see --find EditText`, `keyevent 123`. 49 of them are in the compose cells — the stack where hybrid's perception tokens run furthest above bare. `parse()` already read `focused` off every node; `render()` printed every other state but that one, so the precondition of the three text verbs was the one fact a look could not answer.

### Did the acli arm use accessibility-cli?

12/12 acli runs invoked the binary. 84 of 811 invocations went through a shell wrapper the agent defined (`A --llm-query`), not the literal name.

| invocation | calls | share |
|---|---:|---:|
| `accessibility-cli action (tap/type/key/adb-*)` | 585 | 72% |
| `accessibility-cli other` | 190 | 23% |
| `accessibility-cli --llm (whole tree)` | 32 | 4% |
| `accessibility-cli screenshot / annotate` | 3 | 0% |
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
  which cover an unmeasured share of of each arm's `exec` calls: a command run inside a shell script or a
  loop the agent wrote is one event, so counts are a floor, and they are a lower floor for the
  arm that wrapped its tool.
- Raw data: `runs.json` (cell -> session), `metrics.json`, `tasks.json`, `bypass.json`.

