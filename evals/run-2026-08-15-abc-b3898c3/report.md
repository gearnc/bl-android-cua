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
improvised tree tooling, 3/12 did visual CUA,
8 sat in between. Median bare run:
10 screenshots across ~30 tasks. So this mostly measures **the skill vs. visual computer use**, the comparison the plugin README claims — and it is the flattering framing, not the harsh one. Re-check
this split every run before quoting the numbers; it decides which experiment you ran, and it
has flipped between runs of the same matrix.

The opposite failure — completing tasks by writing device state instead of driving the UI
(`adb shell mkdir` for "create a folder") — is counted too: runs touching device state directly,
7/12 hybrid, 5/12 bare, 5/12 acli.
A large imbalance here invalidates the ACU comparison, because one arm is doing less work.

## Headline

| metric | arm | mean | median | cv | p90 | max |
|---|---|---|---|---|---|---|
| ACU | hybrid | 15.8 | 14.7 | 0.36 | 17.0 | 28.4 |
| ACU | bare | 14.3 | 13.4 | 0.40 | 21.1 | 23.5 |
| ACU | acli | 16.9 | 17.9 | 0.27 | 19.9 | 24.3 |
| perception tokens | hybrid | 45,343 | 45,259 | 0.35 | 55,370 | 75,933 |
| perception tokens | bare | 57,679 | 37,898 | 1.03 | 60,272 | 238,832 |
| perception tokens | acli | 48,289 | 45,183 | 0.34 | 70,054 | 76,718 |
| screenshots | hybrid | 5 | 4 | 0.71 | 6 | 15 |
| screenshots | bare | 23 | 10 | 1.66 | 25 | 145 |
| screenshots | acli | 15 | 11 | 0.75 | 17 | 37 |
| tasks done (of ~30) | hybrid | 28.1 | 28.0 | 0.05 | 29.0 | 30.0 |
| tasks done (of ~30) | bare | 28.1 | 28.0 | 0.04 | 29.0 | 30.0 |
| tasks done (of ~30) | acli | 27.9 | 28.0 | 0.04 | 29.0 | 29.0 |

Ratios against bare — ACU: hybrid **1.11x**, acli **1.18x**. Perception tokens:
hybrid **0.79x**, acli **0.84x**. Iterations: hybrid **1.16x**, acli **1.23x**. Exec calls:
hybrid **1.32x**, acli **1.34x**. Tasks done: hybrid **1.00x**, acli **0.99x**.

Worst run by perception tokens — hybrid 75,933 (amaze|hybrid|2), bare 238,832 (seal|bare|2), acli 76,718 (amaze|acli|1).


### ACU by stack

| stack | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 14.8 | 0.12 | 14.1 | 0.45 | 15.7 | 0.17 | 1.06x | 1.12x |
| rn | 10.9 | 0.25 | 10.1 | 0.38 | 15.0 | 0.42 | 1.09x | 1.50x |
| views | 21.7 | 0.26 | 18.7 | 0.19 | 19.8 | 0.17 | 1.16x | 1.06x |
| **all** | 15.8 | 0.36 | 14.3 | 0.40 | 16.9 | 0.27 | 1.11x | 1.18x |

### Perception tokens by stack

| stack | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 45,716 | 0.05 | 84,917 | 1.21 | 46,606 | 0.12 | 0.54x | 0.55x |
| rn | 29,420 | 0.43 | 38,356 | 0.45 | 50,424 | 0.47 | 0.77x | 1.31x |
| views | 60,892 | 0.17 | 49,764 | 0.42 | 47,837 | 0.42 | 1.22x | 0.96x |
| **all** | 45,343 | 0.35 | 57,679 | 1.03 | 48,289 | 0.34 | 0.79x | 0.84x |

### Iterations by stack

| stack | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 167 | 0.16 | 141 | 0.17 | 178 | 0.17 | 1.18x | 1.26x |
| rn | 118 | 0.25 | 110 | 0.35 | 157 | 0.37 | 1.07x | 1.43x |
| views | 240 | 0.24 | 204 | 0.27 | 224 | 0.21 | 1.18x | 1.10x |
| **all** | 175 | 0.36 | 152 | 0.37 | 186 | 0.28 | 1.16x | 1.23x |

### Screenshots by stack

| stack | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 7 | 0.73 | 44 | 1.56 | 10 | 0.55 | 0.17x | 0.24x |
| rn | 3 | 0.39 | 15 | 0.64 | 25 | 0.57 | 0.22x | 1.68x |
| views | 5 | 0.59 | 12 | 0.74 | 9 | 0.51 | 0.42x | 0.77x |
| **all** | 5 | 0.71 | 23 | 1.66 | 15 | 0.75 | 0.22x | 0.63x |

### Tasks done (of ~30) by stack

| stack | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 27.2 | 0.06 | 27.0 | 0.04 | 26.5 | 0.02 | 1.01x | 0.98x |
| rn | 28.8 | 0.02 | 29.0 | 0.03 | 29.0 | 0.00 | 0.99x | 1.00x |
| views | 28.2 | 0.04 | 28.2 | 0.03 | 28.2 | 0.02 | 1.00x | 1.00x |
| **all** | 28.1 | 0.05 | 28.1 | 0.04 | 27.9 | 0.04 | 1.00x | 0.99x |

### ACU by app

| app | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| amaze | 26.4 | 0.11 | 21.7 | 0.04 | 22.1 | 0.14 | 1.21x | 1.02x |
| joplin | 12.5 | 0.12 | 13.2 | 0.17 | 20.4 | 0.06 | 0.95x | 1.55x |
| lesspass | 9.4 | 0.35 | 6.9 | 0.02 | 9.7 | 0.18 | 1.35x | 1.40x |
| markor | 17.0 | 0.00 | 15.7 | 0.02 | 17.5 | 0.09 | 1.09x | 1.12x |
| seal | 16.4 | 0.04 | 17.7 | 0.46 | 16.1 | 0.20 | 0.93x | 0.91x |
| unitto | 13.3 | 0.01 | 10.4 | 0.05 | 15.3 | 0.20 | 1.28x | 1.47x |
| **all** | 15.8 | 0.36 | 14.3 | 0.40 | 16.9 | 0.27 | 1.11x | 1.18x |

### Perception tokens by app

| app | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| amaze | 67,517 | 0.18 | 65,001 | 0.30 | 61,722 | 0.34 | 1.04x | 0.95x |
| joplin | 40,352 | 0.04 | 51,850 | 0.23 | 70,868 | 0.02 | 0.78x | 1.37x |
| lesspass | 18,488 | 0.07 | 24,863 | 0.18 | 29,978 | 0.00 | 0.74x | 1.21x |
| markor | 54,268 | 0.03 | 34,528 | 0.02 | 33,952 | 0.04 | 1.57x | 0.98x |
| seal | 45,259 | 0.00 | 133,548 | 1.11 | 42,377 | 0.04 | 0.34x | 0.32x |
| unitto | 46,174 | 0.09 | 36,286 | 0.18 | 50,835 | 0.07 | 1.27x | 1.40x |
| **all** | 45,343 | 0.35 | 57,679 | 1.03 | 48,289 | 0.34 | 0.79x | 0.84x |

### Billed input tokens (what ACU tracks)

| | hybrid | bare | acli |
|---|---:|---:|---:|
| billed input, median | 12.93 Mtok | 10.82 Mtok | 15.07 Mtok |
| billed input, mean | 13.50 Mtok | 11.43 Mtok | 14.39 Mtok |
| peak resident context | 114,667 | 110,950 | 115,900 |
| turns | 175 | 152 | 186 |
| perception tokens | 45,343 | 57,679 | 48,289 |

Billed input is the integral of context size over turns, so a token added at turn *i* is charged again at every turn after it. Against bare on the median run: hybrid **1.20x**, acli **1.39x** — a perception ratio does not carry into cost, because a whole run's perception spend is a fraction of a percent of what it bills.

### Where the ACU goes

| per run | hybrid | bare | acli |
|---|---:|---:|---:|
| commands before the first action | 6.92 | 8.83 | 18.92 |
| of those, writing its own tooling | 0.00 | 0.50 | 0.83 |
| looks/task | 3.32 | 2.20 | 3.71 |
| perception tokens per look | 587 | 21,120 | 608 |
| actions per look | 2.21 | 3.24 | 0.82 |
| blind multi-action commands | 17.25 | 16.08 | 4.58 |
| turns/task | 6.29 | 5.44 | 6.70 |
| ACU/turn | 0.0906 | 0.0937 | 0.0906 |
| ACU/task | 0.57 | 0.51 | 0.60 |

Across the 24 hybrid/bare cells, one extra look per task costs **0.062 ACU per task** (1.74 ACU over a 28-task run) — the strongest per-cell predictor of ACU after turn count itself. hybrid takes 3.32 looks per task against bare's 2.20, which alone prices at +1.96 ACU per run against an observed gap of +1.53. The cheaper look is spent on more looking: bootstrapping the improvised tooling is 0.5 commands of a 152-turn run, so there is no setup tax to amortise.

### Which observation verb the hybrid arm typed

| verb | calls | share |
|---|---:|---:|
| `hd see --find` | 575 | 56% |
| `hd see (delta on a re-observation)` | 362 | 35% |
| `hd see --full` | 57 | 6% |
| `hd see -q (capture, print nothing)` | 39 | 4% |

Of the 362 plain `hd see` re-observations, 160 (44%) directly followed a `--find` or `-q` and 8 a `--full`. `--find` and `-q` render the whole tree but print only the matches (or nothing), so this revision keys the diff baseline off the rendering the caller was SHOWN: those re-observations diff against the last tree that actually reached the agent rather than answering `# no change since the last see` about a screen it has never seen. `evals/test_seen_baseline.py` is the regression; re-read this share every run, since it decides how much that behaviour is worth.


### Replacing a value that is already in a field

| | hybrid | bare | acli |
|---|---:|---:|---:|
| hand-rolled deletion loops | 6 | 5 | 12 |
| runs doing it | 4/12 | 4/12 | 5/12 |

Every arm meets the same fields, and none of the three tools had a verb for emptying one, so the agents sent `KEYCODE_MOVE_END` and a guessed number of backspaces. The count is not knowable from outside the tree — the guesses escalate within a run (`seal|hybrid|1`: 20, 30, 10, 30, 30, 40, 20, 40, 20) and a low one leaves the tail of the old value fused to the new text. `hd type "x" -r` takes the count from the focused node's own text; `evals/test_replace.py` prices it against the guess.

### Finding the focused field

| | hybrid | bare | acli |
|---|---:|---:|---:|
| focus-hunting commands | 67 | 20 | 24 |
| runs doing it | 12/12 | 8/12 | 6/12 |

The hybrid arm spent 67 commands in 12/12 runs answering a question its own tree already knew the answer to: `hd see --full | grep -i edit`, `hd see --find EditText`, `keyevent 123`. 30 of them are in the compose cells — the stack where hybrid's perception tokens run furthest above bare. `parse()` already read `focused` off every node; `render()` printed every other state but that one, so the precondition of the three text verbs was the one fact a look could not answer.

### Looks bought to turn a label into an index

| | hybrid | bare | acli |
|---|---:|---:|---:|
| look-only commands | 252 | 0 | 0 |
| ...followed by nothing but an index tap | 100 | 0 | 0 |
| runs doing it | 11/12 | 0/12 | 0/12 |
| actions taken by selector/label | 127 | 0 | 84 |

100 of the hybrid arm's 252 look-only commands, in 11/12 runs, were followed by nothing but `hd tap <index>` — a turn spent numbering a target the agent could already name. The acli arm never paid it: it acts on a selector (84 `--click`/`--type` invocations) and lets its tool resolve the label. `hd tap "PAT"` is hd's form of that and was typed on 126 of the hybrid arm's 781 taps (16%) — documented but under-typed, so hd names it itself after a look that bought nothing but an index (`evals/test_tap_hint.py`; `evals/test_tap_label.py` prices the verb).

### Did the acli arm use accessibility-cli?

12/12 acli runs invoked the binary.

| invocation | calls | share |
|---|---:|---:|
| `accessibility-cli action (tap/type/key/adb-*)` | 480 | 57% |
| `accessibility-cli other` | 301 | 36% |
| `accessibility-cli --llm (whole tree)` | 49 | 6% |
| `accessibility-cli screenshot / annotate` | 7 | 1% |

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

