# android-hybrid-navigation vs. unguided agent vs. the raw method — 36-run blinded eval

**Matrix.** 6 apps x 3 arms x 2 replicates = 36 child sessions,
Normal capability, ~30 machine-verifiable tasks per app, one app per session. Apps:
amaze, joplin, lesspass, markor, seal, unitto. Arms: hybrid, bare, raw. Every run booted the same emulator snapshot
(Android 14, API 34, 720x1280 @320dpi, F-Droid APKs preinstalled) and ended with a fixed `adb`
state dump, so grading is not self-report. Arms were blind and differ by exactly one paragraph:
hybrid was told only to use whatever tooling it has, bare was forbidden both skills, raw was forbidden `android-hybrid-navigation` and told to read `android-raw-navigation`'s SKILL.md instead. Ratios are against **bare**.

## What the bare arm actually does

**Mostly it is not screenshot-driven CUA.** Denied the skill, agents sometimes reinvent it — a bare session may write a
`uiautomator dump` wrapper (`ui.sh`, `t.sh`, `ui.py`) in its first minute and grep it — and
sometimes just looks at the screen. Counting a run as *improvised tree tooling* at
<= 5 screenshots and as *visual CUA* at >= 20: 3/12 bare runs
improvised tree tooling, 2/12 did visual CUA,
7 sat in between. Median bare run:
10 screenshots across ~30 tasks. So this mostly measures **the skill vs. agent-improvised tree tooling**, not the skill vs. looking at the screen — a harsher bar than the README's. Re-check
this split every run before quoting the numbers; it decides which experiment you ran, and it
has flipped between runs of the same matrix.

The opposite failure — completing tasks by writing device state instead of driving the UI
(`adb shell mkdir` for "create a folder") — is counted too: runs touching device state directly,
4/12 hybrid, 5/12 bare, 6/12 raw.
A large imbalance here invalidates the ACU comparison, because one arm is doing less work.

## Headline

| metric | arm | mean | median | cv | p90 | max |
|---|---|---|---|---|---|---|
| ACU | hybrid | 13.9 | 15.0 | 0.33 | 16.1 | 21.8 |
| ACU | bare | 13.3 | 12.4 | 0.47 | 20.1 | 24.7 |
| ACU | raw | 12.0 | 11.3 | 0.48 | 15.9 | 24.9 |
| perception tokens | hybrid | 42,480 | 44,566 | 0.29 | 52,429 | 60,731 |
| perception tokens | bare | 37,042 | 33,457 | 0.56 | 46,958 | 78,076 |
| perception tokens | raw | 19,655 | 21,798 | 0.31 | 23,602 | 29,651 |
| screenshots | hybrid | 7.2 | 6.0 | 0.63 | 12.0 | 16.0 |
| screenshots | bare | 17.4 | 10.5 | 1.43 | 18.0 | 94.0 |
| screenshots | raw | 2.8 | 2.5 | 0.58 | 3.0 | 7.0 |
| tasks done (of ~30) | hybrid | 27.7 | 28.5 | 0.07 | 29.0 | 29.0 |
| tasks done (of ~30) | bare | 28.1 | 28.0 | 0.04 | 29.0 | 30.0 |
| tasks done (of ~30) | raw | 28.2 | 28.0 | 0.03 | 29.0 | 30.0 |

Ratios against bare — ACU: hybrid **1.04x**, raw **0.91x**. Perception tokens:
hybrid **1.15x**, raw **0.53x**. Iterations: hybrid **1.05x**, raw **0.87x**. Exec calls:
hybrid **1.13x**, raw **0.94x**. Tasks done: hybrid **0.99x**, raw **1.01x**.

Worst run by perception tokens — hybrid 60,731 (amaze|hybrid|1), bare 78,076 (amaze|bare|1), raw 29,651 (markor|raw|2).


### ACU by stack

| stack | hybrid mean | cv | bare mean | cv | raw mean | cv | hybrid/bare | raw/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 13.6 | 0.23 | 10.3 | 0.25 | 10.8 | 0.13 | 1.32x | 1.04x |
| rn | 10.9 | 0.48 | 11.2 | 0.59 | 7.0 | 0.42 | 0.97x | 0.62x |
| views | 17.0 | 0.21 | 18.2 | 0.37 | 18.2 | 0.26 | 0.93x | 1.00x |
| **all** | 13.9 | 0.33 | 13.3 | 0.47 | 12.0 | 0.48 | 1.04x | 0.91x |

### Perception tokens by stack

| stack | hybrid mean | cv | bare mean | cv | raw mean | cv | hybrid/bare | raw/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 40,675 | 0.07 | 30,775 | 0.23 | 20,191 | 0.17 | 1.32x | 0.66x |
| rn | 35,040 | 0.50 | 23,072 | 0.65 | 13,897 | 0.40 | 1.52x | 0.60x |
| views | 51,725 | 0.13 | 57,277 | 0.36 | 24,876 | 0.13 | 0.90x | 0.43x |
| **all** | 42,480 | 0.29 | 37,042 | 0.56 | 19,655 | 0.31 | 1.15x | 0.53x |

### Iterations by stack

| stack | hybrid mean | cv | bare mean | cv | raw mean | cv | hybrid/bare | raw/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 165 | 0.23 | 141 | 0.24 | 134 | 0.12 | 1.17x | 0.95x |
| rn | 138 | 0.43 | 130 | 0.52 | 87 | 0.41 | 1.06x | 0.67x |
| views | 213 | 0.22 | 221 | 0.38 | 208 | 0.30 | 0.96x | 0.94x |
| **all** | 172 | 0.32 | 164 | 0.44 | 143 | 0.45 | 1.05x | 0.87x |

### Screenshots by stack

| stack | hybrid mean | cv | bare mean | cv | raw mean | cv | hybrid/bare | raw/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 8.2 | 0.66 | 10.5 | 0.56 | 3.2 | 0.81 | 0.79x | 0.31x |
| rn | 7.8 | 0.64 | 29.8 | 1.45 | 2.0 | 0.41 | 0.26x | 0.07x |
| views | 5.8 | 0.72 | 12.0 | 0.68 | 3.0 | 0.27 | 0.48x | 0.25x |
| **all** | 7.2 | 0.63 | 17.4 | 1.43 | 2.8 | 0.58 | 0.42x | 0.16x |

### Tasks done (of ~30) by stack

| stack | hybrid mean | cv | bare mean | cv | raw mean | cv | hybrid/bare | raw/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 26.2 | 0.10 | 27.0 | 0.03 | 27.2 | 0.02 | 0.97x | 1.01x |
| rn | 28.0 | 0.04 | 28.8 | 0.03 | 28.8 | 0.02 | 0.97x | 1.00x |
| views | 28.8 | 0.02 | 28.5 | 0.02 | 28.8 | 0.03 | 1.01x | 1.01x |
| **all** | 27.7 | 0.07 | 28.1 | 0.04 | 28.2 | 0.03 | 0.99x | 1.01x |

### ACU by app

| app | hybrid mean | cv | bare mean | cv | raw mean | cv | hybrid/bare | raw/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| amaze | 19.5 | 0.17 | 24.0 | 0.04 | 16.9 | 0.08 | 0.81x | 0.70x |
| joplin | 15.5 | 0.05 | 16.3 | 0.33 | 9.4 | 0.18 | 0.95x | 0.58x |
| lesspass | 6.4 | 0.12 | 6.2 | 0.06 | 4.6 | 0.06 | 1.03x | 0.74x |
| markor | 14.4 | 0.08 | 12.4 | 0.00 | 19.6 | 0.38 | 1.16x | 1.58x |
| seal | 15.3 | 0.05 | 12.2 | 0.19 | 11.4 | 0.04 | 1.26x | 0.94x |
| unitto | 12.0 | 0.36 | 8.5 | 0.08 | 10.2 | 0.21 | 1.41x | 1.20x |
| **all** | 13.9 | 0.33 | 13.3 | 0.47 | 12.0 | 0.48 | 1.04x | 0.91x |

### Perception tokens by app

| app | hybrid mean | cv | bare mean | cv | raw mean | cv | hybrid/bare | raw/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| amaze | 56,580 | 0.10 | 74,199 | 0.07 | 23,258 | 0.05 | 0.76x | 0.31x |
| joplin | 49,972 | 0.13 | 26,880 | 0.93 | 18,280 | 0.23 | 1.86x | 0.68x |
| lesspass | 20,108 | 0.07 | 19,264 | 0.02 | 9,514 | 0.05 | 1.04x | 0.49x |
| markor | 46,870 | 0.08 | 40,356 | 0.23 | 26,494 | 0.17 | 1.16x | 0.66x |
| seal | 39,680 | 0.03 | 25,354 | 0.15 | 20,034 | 0.18 | 1.57x | 0.79x |
| unitto | 41,670 | 0.11 | 36,196 | 0.12 | 20,348 | 0.23 | 1.15x | 0.56x |
| **all** | 42,480 | 0.29 | 37,042 | 0.56 | 19,655 | 0.31 | 1.15x | 0.53x |

### Billed input tokens (what ACU tracks)

| | hybrid | bare | raw |
|---|---:|---:|---:|
| billed input, median | 14.19 Mtok | 11.07 Mtok | 9.55 Mtok |
| billed input, mean | 13.23 Mtok | 12.23 Mtok | 10.18 Mtok |
| peak resident context | 118,533 | 110,104 | 102,010 |
| turns | 172 | 164 | 143 |
| perception tokens | 42,480 | 37,042 | 19,655 |

Billed input is the integral of context size over turns, so a token added at turn *i* is charged again at every turn after it. Against bare on the median run: hybrid **1.28x**, raw **0.86x** — a perception ratio does not carry into cost, because a whole run's perception spend is a fraction of a percent of what it bills.

### Where the ACU goes

| per run | hybrid | bare | raw |
|---|---:|---:|---:|
| commands before the first action | 5.42 | 6.00 | 4.42 |
| of those, writing its own tooling | 0.08 | 0.50 | 0.08 |
| looks/task | 3.57 | 2.87 | 2.44 |
| perception tokens per look | 511 | 862 | 337 |
| actions per look | 2.22 | 1.90 | 2.07 |
| blind multi-action commands | 16.83 | 17.58 | 21.25 |
| turns/task | 6.24 | 5.84 | 5.06 |
| ACU/turn | 0.0800 | 0.0802 | 0.0830 |
| ACU/task | 0.50 | 0.47 | 0.42 |

Across the 24 hybrid/bare cells, one extra look per task costs **0.087 ACU per task** (2.43 ACU over a 28-task run) — the strongest per-cell predictor of ACU after turn count itself. hybrid takes 3.57 looks per task against bare's 2.87, which alone prices at +1.72 ACU per run against an observed gap of +0.85. The cheaper look is spent on more looking: bootstrapping the improvised tooling is 0.5 commands of a 164-turn run, so there is no setup tax to amortise.

### Which observation verb the hybrid arm typed

| verb | calls | share |
|---|---:|---:|
| `hd see (delta on a re-observation)` | 477 | 44% |
| `hd see --find` | 464 | 43% |
| `hd see --full` | 89 | 8% |
| `hd see -q (capture, print nothing)` | 49 | 5% |
| `hd see --no-diff (opt out of the delta)` | 1 | 0% |

Of the 477 plain `hd see` re-observations, 148 (31%) directly followed a `--find` or `-q` and 30 a `--full`. `--find` and `-q` render the whole tree but print only the matches (or nothing), so this revision keys the diff baseline off the rendering the caller was SHOWN: those re-observations diff against the last tree that actually reached the agent rather than answering `# no change since the last see` about a screen it has never seen. `evals/test_seen_baseline.py` is the regression; re-read this share every run, since it decides how much that behaviour is worth.


### Replacing a value that is already in a field

| | hybrid | bare | raw |
|---|---:|---:|---:|
| hand-rolled deletion loops | 5 | 6 | 9 |
| runs doing it | 3/12 | 4/12 | 5/12 |

Every arm meets the same fields, and none of the three tools had a verb for emptying one, so the agents sent `KEYCODE_MOVE_END` and a guessed number of backspaces. The count is not knowable from outside the tree — the guesses escalate within a run (`seal|hybrid|1`: 20, 30, 10, 30, 30, 40, 20, 40, 20) and a low one leaves the tail of the old value fused to the new text. `hd type "x" -r` takes the count from the focused node's own text; `evals/test_replace.py` prices it against the guess.

### Finding the focused field

| | hybrid | bare | raw |
|---|---:|---:|---:|
| focus-hunting commands | 56 | 32 | 38 |
| runs doing it | 10/12 | 11/12 | 11/12 |

The hybrid arm spent 56 commands in 10/12 runs answering a question its own tree already knew the answer to: `hd see --full | grep -i edit`, `hd see --find EditText`, `keyevent 123`. 26 of them are in the rn cells — the stack where hybrid's perception tokens run furthest above bare. `parse()` already read `focused` off every node; `render()` printed every other state but that one, so the precondition of the three text verbs was the one fact a look could not answer.

### Looks bought to turn a label into an index

| | hybrid | bare | raw |
|---|---:|---:|---:|
| look-only commands | 291 | 0 | 0 |
| ...followed by nothing but an index tap | 147 | 0 | 0 |
| runs doing it | 11/12 | 0/12 | 0/12 |
| actions taken by selector/label | 1 | 0 | 0 |

147 of the hybrid arm's 291 look-only commands, in 11/12 runs, were followed by nothing but `hd tap <index>` — a turn spent numbering a target the agent could already name. The other arms never pay it, because they tap coordinates the tree already printed and never index anything. `hd tap "PAT"` is hd's form of acting by name and was typed on 0 of the hybrid arm's 917 taps (0%) — documented but under-typed, so hd names it itself after a look that bought nothing but an index (`evals/test_tap_hint.py`; `evals/test_tap_label.py` prices the verb).


### Did the raw arm use the method it was handed?

12/12 raw runs drove the emulator with the wrapper (`python3 ~/ui.py see`, `uiautomator dump`), 781 invocations in total, first used at command 2-13 of the run. 0/12 runs invoked `hd` (contamination).

| cell | wrapper invocations | first at command | `hd` invocations |
|---|---:|---:|---:|
| amaze\|raw\|1 | 102 | 5 | 0 |
| amaze\|raw\|2 | 65 | 4 | 0 |
| joplin\|raw\|1 | 61 | 4 | 0 |
| joplin\|raw\|2 | 50 | 5 | 0 |
| lesspass\|raw\|1 | 10 | 3 | 0 |
| lesspass\|raw\|2 | 13 | 2 | 0 |
| markor\|raw\|1 | 77 | 4 | 0 |
| markor\|raw\|2 | 70 | 13 | 0 |
| seal\|raw\|1 | 105 | 3 | 0 |
| seal\|raw\|2 | 99 | 2 | 0 |
| unitto\|raw\|1 | 60 | 6 | 0 |
| unitto\|raw\|2 | 69 | 7 | 0 |

A cell that never typed the method, or that reached for `hd`, measures something other than the arm it is labelled as and must be dropped before any raw ratio is quoted.

### Did the bare arm rederive the method?

11/12 bare runs wrote or ran a tree-dump wrapper of their own, first at command 2-64. Cells: amaze|bare|1 (163), amaze|bare|2 (136), joplin|bare|2 (50), lesspass|bare|1 (5), lesspass|bare|2 (5), markor|bare|1 (77), markor|bare|2 (80), seal|bare|1 (1), seal|bare|2 (108), unitto|bare|1 (1), unitto|bare|2 (61).

This is the quantity `raw` vs. `bare` prices: where the bare arm did rederive the method, the two arms should converge; where it did not, the gap is the method itself.

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
- Dump validity: the preflight `evals/test_dumps.py` reported no `problems` for any of the six
  apps, but several apps' dump commands exited non-zero (the command reads app files that do not
  exist in a freshly installed app). The script does not fail on that, so the playbook's "rc=0
  for every app" condition was NOT strictly met; the per-app trees themselves dumped and the
  final state dumps graded cleanly, so the matrix stands, but this is a weaker preflight than
  the procedure asks for and `test_dumps.py` should be made to exit non-zero on it.

