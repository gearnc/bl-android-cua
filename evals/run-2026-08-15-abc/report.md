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
10 screenshots across ~30 tasks. So this mostly measures **the skill vs. visual computer use**, the comparison the plugin README claims — and it is the flattering framing, not the harsh one. Re-check
this split every run before quoting the numbers; it decides which experiment you ran, and it
has flipped between runs of the same matrix.

The opposite failure — completing tasks by writing device state instead of driving the UI
(`adb shell mkdir` for "create a folder") — is counted too: runs touching device state directly,
3/12 hybrid, 5/12 bare, 6/12 acli.
A large imbalance here invalidates the ACU comparison, because one arm is doing less work.

## Headline

| metric | arm | mean | median | cv | p90 | max |
|---|---|---|---|---|---|---|
| ACU | hybrid | 15.0 | 14.4 | 0.39 | 16.6 | 27.1 |
| ACU | bare | 15.2 | 12.9 | 0.49 | 22.3 | 31.8 |
| ACU | acli | 16.1 | 15.7 | 0.32 | 17.7 | 25.8 |
| perception tokens | hybrid | 42,218 | 40,222 | 0.41 | 52,327 | 84,019 |
| perception tokens | bare | 50,024 | 36,407 | 0.67 | 60,246 | 130,955 |
| perception tokens | acli | 44,986 | 40,646 | 0.28 | 57,781 | 67,733 |
| screenshots | hybrid | 4.8 | 4.5 | 0.67 | 7.0 | 12.0 |
| screenshots | bare | 19.1 | 10.5 | 1.17 | 25.0 | 84.0 |
| screenshots | acli | 13.4 | 9.5 | 0.76 | 20.0 | 35.0 |
| tasks done (of ~30) | hybrid | 28.2 | 28.0 | 0.05 | 30.0 | 30.0 |
| tasks done (of ~30) | bare | 28.3 | 28.5 | 0.04 | 29.0 | 30.0 |
| tasks done (of ~30) | acli | 27.7 | 28.0 | 0.04 | 29.0 | 29.0 |

Ratios against bare — ACU: hybrid **0.98x**, acli **1.06x**. Perception tokens:
hybrid **0.84x**, acli **0.90x**. Iterations: hybrid **0.99x**, acli **1.06x**. Exec calls:
hybrid **1.08x**, acli **1.10x**. Tasks done: hybrid **1.00x**, acli **0.98x**.

Worst run by perception tokens — hybrid 84,019 (amaze|hybrid|1), bare 130,955 (markor|bare|2), acli 67,733 (joplin|acli|1).


### ACU by stack

| stack | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 14.2 | 0.15 | 13.0 | 0.20 | 14.2 | 0.18 | 1.09x | 1.09x |
| rn | 10.7 | 0.40 | 9.8 | 0.35 | 13.2 | 0.31 | 1.09x | 1.35x |
| views | 20.0 | 0.32 | 22.9 | 0.33 | 20.9 | 0.26 | 0.88x | 0.91x |
| **all** | 15.0 | 0.39 | 15.2 | 0.49 | 16.1 | 0.32 | 0.98x | 1.06x |

### Perception tokens by stack

| stack | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 41,158 | 0.20 | 43,886 | 0.32 | 40,130 | 0.08 | 0.94x | 0.91x |
| rn | 29,896 | 0.45 | 26,410 | 0.36 | 49,708 | 0.38 | 1.13x | 1.88x |
| views | 55,602 | 0.37 | 79,777 | 0.55 | 45,118 | 0.27 | 0.70x | 0.57x |
| **all** | 42,218 | 0.41 | 50,024 | 0.67 | 44,986 | 0.28 | 0.84x | 0.90x |

### Iterations by stack

| stack | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 160 | 0.19 | 148 | 0.14 | 160 | 0.18 | 1.08x | 1.08x |
| rn | 124 | 0.40 | 116 | 0.31 | 140 | 0.28 | 1.08x | 1.21x |
| views | 218 | 0.35 | 244 | 0.37 | 236 | 0.31 | 0.90x | 0.97x |
| **all** | 168 | 0.39 | 169 | 0.46 | 179 | 0.35 | 0.99x | 1.06x |

### Screenshots by stack

| stack | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 5.0 | 0.43 | 17.2 | 0.61 | 8.2 | 0.30 | 0.29x | 0.48x |
| rn | 3.8 | 0.80 | 7.0 | 0.45 | 21.0 | 0.70 | 0.54x | 3.00x |
| views | 5.5 | 0.85 | 33.0 | 1.06 | 11.0 | 0.58 | 0.17x | 0.33x |
| **all** | 4.8 | 0.67 | 19.1 | 1.17 | 13.4 | 0.76 | 0.25x | 0.70x |

### Tasks done (of ~30) by stack

| stack | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 27.2 | 0.04 | 27.2 | 0.04 | 27.0 | 0.04 | 1.00x | 0.99x |
| rn | 28.5 | 0.05 | 28.8 | 0.04 | 28.2 | 0.03 | 0.99x | 0.98x |
| views | 29.0 | 0.05 | 29.0 | 0.03 | 27.8 | 0.05 | 1.00x | 0.96x |
| **all** | 28.2 | 0.05 | 28.3 | 0.04 | 27.7 | 0.04 | 1.00x | 0.98x |

### ACU by app

| app | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| amaze | 25.5 | 0.09 | 28.0 | 0.19 | 25.5 | 0.02 | 0.91x | 0.91x |
| joplin | 14.1 | 0.18 | 12.4 | 0.08 | 16.6 | 0.01 | 1.13x | 1.33x |
| lesspass | 7.2 | 0.20 | 7.2 | 0.37 | 9.8 | 0.22 | 1.01x | 1.37x |
| markor | 14.5 | 0.06 | 17.8 | 0.36 | 16.2 | 0.11 | 0.82x | 0.91x |
| seal | 15.5 | 0.10 | 14.5 | 0.20 | 16.1 | 0.14 | 1.06x | 1.10x |
| unitto | 12.9 | 0.16 | 11.5 | 0.14 | 12.4 | 0.03 | 1.12x | 1.07x |
| **all** | 15.0 | 0.39 | 15.2 | 0.49 | 16.1 | 0.32 | 0.98x | 1.06x |

### Perception tokens by app

| app | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| amaze | 69,111 | 0.31 | 78,244 | 0.36 | 55,312 | 0.06 | 0.88x | 0.71x |
| joplin | 41,014 | 0.11 | 33,280 | 0.24 | 65,850 | 0.04 | 1.23x | 1.98x |
| lesspass | 18,778 | 0.25 | 19,540 | 0.21 | 33,566 | 0.14 | 0.96x | 1.72x |
| markor | 42,092 | 0.24 | 81,310 | 0.86 | 34,925 | 0.06 | 0.52x | 0.43x |
| seal | 38,026 | 0.17 | 45,220 | 0.47 | 37,954 | 0.08 | 0.84x | 0.84x |
| unitto | 44,288 | 0.26 | 42,553 | 0.29 | 42,306 | 0.04 | 1.04x | 0.99x |
| **all** | 42,218 | 0.41 | 50,024 | 0.67 | 44,986 | 0.28 | 0.84x | 0.90x |

### Billed input tokens (what ACU tracks)

| | hybrid | bare | acli |
|---|---:|---:|---:|
| billed input, median | 12.17 Mtok | 10.86 Mtok | 13.52 Mtok |
| billed input, mean | 13.09 Mtok | 12.74 Mtok | 14.15 Mtok |
| peak resident context | 115,183 | 111,372 | 117,262 |
| turns | 168 | 169 | 179 |
| perception tokens | 42,218 | 50,024 | 44,986 |

Billed input is the integral of context size over turns, so a token added at turn *i* is charged again at every turn after it. Against bare on the median run: hybrid **1.12x**, acli **1.25x** — a perception ratio does not carry into cost, because a whole run's perception spend is a fraction of a percent of what it bills.

### Where the ACU goes

| per run | hybrid | bare | acli |
|---|---:|---:|---:|
| commands before the first action | 7.33 | 4.33 | 15.25 |
| of those, writing its own tooling | 0.00 | 0.08 | 0.42 |
| looks/task | 3.24 | 2.38 | 3.08 |
| perception tokens per look | 477 | 1,727 | 817 |
| actions per look | 2.10 | 6.14 | 0.90 |
| blind multi-action commands | 17.50 | 25.67 | 4.08 |
| turns/task | 5.96 | 5.97 | 6.52 |
| ACU/turn | 0.0892 | 0.0889 | 0.0904 |
| ACU/task | 0.53 | 0.54 | 0.59 |

Across the 24 hybrid/bare cells, one extra look per task costs **0.077 ACU per task** (2.15 ACU over a 28-task run) — the strongest per-cell predictor of ACU after turn count itself. hybrid takes 3.24 looks per task against bare's 2.38, which alone prices at +1.85 ACU per run against an observed gap of -0.13. The cheaper look is spent on more looking: bootstrapping the improvised tooling is 0.1 commands of a 169-turn run, so there is no setup tax to amortise.

### Which observation verb the hybrid arm typed

| verb | calls | share |
|---|---:|---:|
| `hd see --find` | 525 | 52% |
| `hd see (delta on a re-observation)` | 439 | 43% |
| `hd see --full` | 33 | 3% |
| `hd see -q (capture, print nothing)` | 21 | 2% |

Of the 439 plain `hd see` re-observations, 184 (42%) directly followed a `--find` or `-q` and 11 a `--full`. `--find` and `-q` render the whole tree but print only the matches (or nothing), so this revision keys the diff baseline off the rendering the caller was SHOWN: those re-observations diff against the last tree that actually reached the agent rather than answering `# no change since the last see` about a screen it has never seen. `evals/test_seen_baseline.py` is the regression; re-read this share every run, since it decides how much that behaviour is worth.


### Replacing a value that is already in a field

| | hybrid | bare | acli |
|---|---:|---:|---:|
| hand-rolled deletion loops | 2 | 7 | 10 |
| runs doing it | 1/12 | 5/12 | 5/12 |

Every arm meets the same fields, and none of the three tools had a verb for emptying one, so the agents sent `KEYCODE_MOVE_END` and a guessed number of backspaces. The count is not knowable from outside the tree — the guesses escalate within a run (`seal|hybrid|1`: 20, 30, 10, 30, 30, 40, 20, 40, 20) and a low one leaves the tail of the old value fused to the new text. `hd type "x" -r` takes the count from the focused node's own text; `evals/test_replace.py` prices it against the guess.

### Finding the focused field

| | hybrid | bare | acli |
|---|---:|---:|---:|
| focus-hunting commands | 54 | 50 | 24 |
| runs doing it | 10/12 | 11/12 | 8/12 |

The hybrid arm spent 54 commands in 10/12 runs answering a question its own tree already knew the answer to: `hd see --full | grep -i edit`, `hd see --find EditText`, `keyevent 123`. 30 of them are in the rn cells — the stack where hybrid's perception tokens run furthest above bare. `parse()` already read `focused` off every node; `render()` printed every other state but that one, so the precondition of the three text verbs was the one fact a look could not answer.

### Looks bought to turn a label into an index

| | hybrid | bare | acli |
|---|---:|---:|---:|
| look-only commands | 236 | 0 | 0 |
| ...followed by nothing but an index tap | 115 | 0 | 0 |
| runs doing it | 12/12 | 0/12 | 0/12 |
| actions taken by selector/label | 3 | 2 | 195 |

115 of the hybrid arm's 236 look-only commands, in 12/12 runs, were followed by nothing but `hd tap <index>` — a turn spent numbering a target the agent could already name. The acli arm never paid it: it acts on a selector (195 `--click`/`--type` invocations) and lets its tool resolve the label. `hd tap "PAT"` closes that gap; `evals/test_tap_label.py` prices it.

### Did the acli arm use accessibility-cli?

12/12 acli runs invoked the binary. 308 of 1,001 invocations went through a shell wrapper the agent defined (`A --llm-query`), not the literal name.

| invocation | calls | share |
|---|---:|---:|
| `accessibility-cli action (tap/type/key/adb-*)` | 682 | 68% |
| `accessibility-cli other` | 263 | 26% |
| `accessibility-cli --llm (whole tree)` | 48 | 5% |
| `accessibility-cli screenshot / annotate` | 7 | 1% |
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

