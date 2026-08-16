# android-hybrid-navigation vs. unguided agent vs. the raw method — 36-run blinded eval

**Matrix.** 6 apps x 3 arms x 2 replicates = 36 child sessions,
Normal capability, ~30 machine-verifiable tasks per app, one app per session. Apps:
amaze, joplin, lesspass, markor, seal, unitto. Arms: hybrid, bare, raw. Every run booted the same emulator snapshot
(Android 14, API 34, 720x1280 @320dpi, F-Droid APKs preinstalled) and ended with a fixed `adb`
state dump, so grading is not self-report. Arms were blind and differ by exactly one paragraph:
hybrid was told only to use whatever tooling it has, bare was forbidden both skills, raw was forbidden `android-hybrid-navigation` and told to read `android-raw-navigation`'s SKILL.md instead. Ratios are against **bare**.

## What the bare arm actually does

**Mostly it IS screenshot-driven CUA.** Denied the skill, agents sometimes reinvent it — a bare session may write a
`uiautomator dump` wrapper (`ui.sh`, `t.sh`, `ui.py`) in its first minute and grep it — and
sometimes just looks at the screen. Counting a run as *improvised tree tooling* at
<= 5 screenshots and as *visual CUA* at >= 20: 0/12 bare runs
improvised tree tooling, 10/12 did visual CUA,
2 sat in between. Median bare run:
100 screenshots across ~30 tasks. So this mostly measures **the skill vs. visual computer use**, the comparison the plugin README claims — and it is the flattering framing, not the harsh one. Re-check
this split every run before quoting the numbers; it decides which experiment you ran, and it
has flipped between runs of the same matrix.

The opposite failure — completing tasks by writing device state instead of driving the UI
(`adb shell mkdir` for "create a folder") — is counted too: runs touching device state directly,
7/12 hybrid, 5/12 bare, 7/12 raw.
A large imbalance here invalidates the ACU comparison, because one arm is doing less work.

## Headline

| metric | arm | mean | median | cv | p90 | max |
|---|---|---|---|---|---|---|
| ACU | hybrid | 16.5 | 14.4 | 0.36 | 19.8 | 30.3 |
| ACU | bare | 18.7 | 17.5 | 0.37 | 23.4 | 35.7 |
| ACU | raw | 11.9 | 12.2 | 0.36 | 13.9 | 20.5 |
| perception tokens | hybrid | 51,494 | 46,234 | 0.44 | 63,965 | 91,663 |
| perception tokens | bare | 170,645 | 155,402 | 1.03 | 228,743 | 650,887 |
| perception tokens | raw | 20,831 | 21,984 | 0.26 | 24,431 | 30,846 |
| screenshots | hybrid | 4 | 4 | 0.48 | 6 | 9 |
| screenshots | bare | 123 | 100 | 1.05 | 139 | 506 |
| screenshots | raw | 3 | 2 | 0.71 | 4 | 6 |
| tasks done (of ~30) | hybrid | 27.8 | 28.0 | 0.06 | 29.0 | 30.0 |
| tasks done (of ~30) | bare | 28.2 | 29.0 | 0.05 | 29.0 | 30.0 |
| tasks done (of ~30) | raw | 27.5 | 28.0 | 0.06 | 29.0 | 29.0 |

Ratios against bare — ACU: hybrid **0.88x**, raw **0.64x**. Perception tokens:
hybrid **0.30x**, raw **0.12x**. Iterations: hybrid **1.10x**, raw **0.86x**. Exec calls:
hybrid **2.53x**, raw **1.96x**. Tasks done: hybrid **0.99x**, raw **0.97x**.

Worst run by perception tokens — hybrid 91,663 (amaze|hybrid|2), bare 650,887 (markor|bare|1), raw 30,846 (amaze|raw|1).


### ACU by stack

| stack | hybrid mean | cv | bare mean | cv | raw mean | cv | hybrid/bare | raw/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 14.6 | 0.14 | 16.1 | 0.12 | 11.2 | 0.20 | 0.91x | 0.70x |
| rn | 11.7 | 0.24 | 13.9 | 0.29 | 8.5 | 0.36 | 0.84x | 0.61x |
| views | 23.1 | 0.22 | 26.0 | 0.25 | 16.1 | 0.23 | 0.89x | 0.62x |
| **all** | 16.5 | 0.36 | 18.7 | 0.37 | 11.9 | 0.36 | 0.88x | 0.64x |

### Perception tokens by stack

| stack | hybrid mean | cv | bare mean | cv | raw mean | cv | hybrid/bare | raw/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 46,308 | 0.14 | 160,806 | 0.31 | 21,459 | 0.15 | 0.29x | 0.13x |
| rn | 32,380 | 0.44 | 67,110 | 1.20 | 16,223 | 0.36 | 0.48x | 0.24x |
| views | 75,793 | 0.24 | 284,018 | 0.95 | 24,812 | 0.17 | 0.27x | 0.09x |
| **all** | 51,494 | 0.44 | 170,645 | 1.03 | 20,831 | 0.26 | 0.30x | 0.12x |

### Iterations by stack

| stack | hybrid mean | cv | bare mean | cv | raw mean | cv | hybrid/bare | raw/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 164 | 0.15 | 153 | 0.09 | 136 | 0.19 | 1.08x | 0.89x |
| rn | 130 | 0.25 | 137 | 0.16 | 106 | 0.35 | 0.95x | 0.77x |
| views | 248 | 0.20 | 203 | 0.31 | 180 | 0.24 | 1.22x | 0.89x |
| **all** | 181 | 0.34 | 164 | 0.28 | 141 | 0.33 | 1.10x | 0.86x |

### Screenshots by stack

| stack | hybrid mean | cv | bare mean | cv | raw mean | cv | hybrid/bare | raw/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 5 | 0.50 | 101 | 0.26 | 3 | 0.68 | 0.05x | 0.03x |
| rn | 4 | 0.41 | 48 | 1.01 | 2 | 0.41 | 0.08x | 0.04x |
| views | 4 | 0.55 | 220 | 0.87 | 2 | 0.95 | 0.02x | 0.01x |
| **all** | 4 | 0.48 | 123 | 1.05 | 3 | 0.71 | 0.04x | 0.02x |

### Tasks done (of ~30) by stack

| stack | hybrid mean | cv | bare mean | cv | raw mean | cv | hybrid/bare | raw/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 26.2 | 0.06 | 26.8 | 0.05 | 26.0 | 0.07 | 0.98x | 0.97x |
| rn | 28.8 | 0.04 | 29.2 | 0.02 | 28.2 | 0.03 | 0.98x | 0.97x |
| views | 28.5 | 0.02 | 28.8 | 0.04 | 28.2 | 0.02 | 0.99x | 0.98x |
| **all** | 27.8 | 0.06 | 28.2 | 0.05 | 27.5 | 0.06 | 0.99x | 0.97x |

### ACU by app

| app | hybrid mean | cv | bare mean | cv | raw mean | cv | hybrid/bare | raw/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| amaze | 26.5 | 0.21 | 22.5 | 0.12 | 19.1 | 0.10 | 1.18x | 0.85x |
| joplin | 13.7 | 0.11 | 15.2 | 0.34 | 10.7 | 0.24 | 0.90x | 0.71x |
| lesspass | 9.7 | 0.24 | 12.6 | 0.31 | 6.2 | 0.19 | 0.77x | 0.50x |
| markor | 19.8 | 0.00 | 29.5 | 0.29 | 13.0 | 0.00 | 0.67x | 0.44x |
| seal | 15.9 | 0.15 | 17.5 | 0.06 | 12.9 | 0.11 | 0.90x | 0.74x |
| unitto | 13.3 | 0.01 | 14.6 | 0.07 | 9.4 | 0.04 | 0.91x | 0.64x |
| **all** | 16.5 | 0.36 | 18.7 | 0.37 | 11.9 | 0.36 | 0.88x | 0.64x |

### Perception tokens by app

| app | hybrid mean | cv | bare mean | cv | raw mean | cv | hybrid/bare | raw/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| amaze | 91,082 | 0.01 | 239,827 | 0.07 | 27,638 | 0.16 | 0.38x | 0.12x |
| joplin | 44,585 | 0.00 | 110,796 | 0.98 | 20,680 | 0.20 | 0.40x | 0.19x |
| lesspass | 20,176 | 0.08 | 23,422 | 0.28 | 11,766 | 0.17 | 0.86x | 0.50x |
| markor | 60,504 | 0.08 | 328,210 | 1.39 | 21,984 | 0.04 | 0.18x | 0.07x |
| seal | 44,643 | 0.10 | 203,108 | 0.03 | 22,804 | 0.10 | 0.22x | 0.11x |
| unitto | 47,972 | 0.21 | 118,505 | 0.05 | 20,114 | 0.20 | 0.40x | 0.17x |
| **all** | 51,494 | 0.44 | 170,645 | 1.03 | 20,831 | 0.26 | 0.30x | 0.12x |

### Billed input tokens (what ACU tracks)

| | hybrid | bare | raw |
|---|---:|---:|---:|
| billed input, median | 12.94 Mtok | 11.33 Mtok | 10.51 Mtok |
| billed input, mean | 14.10 Mtok | 12.60 Mtok | 10.06 Mtok |
| peak resident context | 115,601 | 103,811 | 103,961 |
| turns | 181 | 164 | 141 |
| perception tokens | 51,494 | 170,645 | 20,831 |

Billed input is the integral of context size over turns, so a token added at turn *i* is charged again at every turn after it. Against bare on the median run: hybrid **1.14x**, raw **0.93x** — a perception ratio does not carry into cost, because a whole run's perception spend is a fraction of a percent of what it bills.

### Where the ACU goes

| per run | hybrid | bare | raw |
|---|---:|---:|---:|
| commands before the first action | 6.25 | 10.33 | 3.58 |
| of those, writing its own tooling | 0.00 | 0.17 | 0.08 |
| looks/task | 3.27 | 0.70 | 2.90 |
| perception tokens per look | 603 | 144,751 | 282 |
| actions per look | 1.88 | 21.22 | 1.96 |
| blind multi-action commands | 15.00 | 10.83 | 20.92 |
| turns/task | 6.50 | 5.82 | 5.14 |
| ACU/turn | 0.0906 | 0.1122 | 0.0838 |
| ACU/task | 0.59 | 0.66 | 0.43 |

Across the 24 hybrid/bare cells, one extra look per task costs **0.003 ACU per task** (0.08 ACU over a 28-task run) — the strongest per-cell predictor of ACU after turn count itself. hybrid takes 3.27 looks per task against bare's 0.70, which alone prices at +0.20 ACU per run against an observed gap of -1.97. The cheaper look is spent on more looking: bootstrapping the improvised tooling is 0.2 commands of a 164-turn run, so there is no setup tax to amortise.

### Which observation verb the hybrid arm typed

| verb | calls | share |
|---|---:|---:|
| `hd see --find` | 525 | 54% |
| `hd see (delta on a re-observation)` | 383 | 40% |
| `hd see --full` | 36 | 4% |
| `hd see -q (capture, print nothing)` | 23 | 2% |
| `hd see --no-diff (opt out of the delta)` | 1 | 0% |

Of the 383 plain `hd see` re-observations, 157 (41%) directly followed a `--find` or `-q` and 9 a `--full`. `--find` and `-q` render the whole tree but print only the matches (or nothing), so this revision keys the diff baseline off the rendering the caller was SHOWN: those re-observations diff against the last tree that actually reached the agent rather than answering `# no change since the last see` about a screen it has never seen. `evals/test_seen_baseline.py` is the regression; re-read this share every run, since it decides how much that behaviour is worth.


### Replacing a value that is already in a field

| | hybrid | bare | raw |
|---|---:|---:|---:|
| hand-rolled deletion loops | 2 | 12 | 22 |
| runs doing it | 2/12 | 6/12 | 9/12 |

Every arm meets the same fields, and none of the three tools had a verb for emptying one, so the agents sent `KEYCODE_MOVE_END` and a guessed number of backspaces. The count is not knowable from outside the tree — the guesses escalate within a run (`seal|hybrid|1`: 20, 30, 10, 30, 30, 40, 20, 40, 20) and a low one leaves the tail of the old value fused to the new text. `hd type "x" -r` takes the count from the focused node's own text; `evals/test_replace.py` prices it against the guess.

### Finding the focused field

| | hybrid | bare | raw |
|---|---:|---:|---:|
| focus-hunting commands | 83 | 22 | 56 |
| runs doing it | 12/12 | 7/12 | 11/12 |

The hybrid arm spent 83 commands in 12/12 runs answering a question its own tree already knew the answer to: `hd see --full | grep -i edit`, `hd see --find EditText`, `keyevent 123`. 38 of them are in the compose cells — the stack where hybrid's perception tokens run furthest above bare. `parse()` already read `focused` off every node; `render()` printed every other state but that one, so the precondition of the three text verbs was the one fact a look could not answer.

### Looks bought to turn a label into an index

| | hybrid | bare | raw |
|---|---:|---:|---:|
| look-only commands | 309 | 0 | 0 |
| ...followed by nothing but an index tap | 108 | 0 | 0 |
| runs doing it | 12/12 | 0/12 | 0/12 |
| actions taken by selector/label | 227 | 0 | 1 |

108 of the hybrid arm's 309 look-only commands, in 12/12 runs, were followed by nothing but `hd tap <index>` — a turn spent numbering a target the agent could already name. The other arms never pay it, because they tap coordinates the tree already printed and never index anything. `hd tap "PAT"` is hd's form of acting by name and was typed on 227 of the hybrid arm's 925 taps (25%) — documented but under-typed, so hd names it itself after a look that bought nothing but an index (`evals/test_tap_hint.py`; `evals/test_tap_label.py` prices the verb).


### Did the raw arm use the method it was handed?

12/12 raw runs drove the emulator with the wrapper (`python3 ~/ui.py see`, `uiautomator dump`), 908 invocations in total, first used at command 2-11 of the run. 0/12 runs invoked `hd` (contamination).

| cell | wrapper invocations | first at command | `hd` invocations |
|---|---:|---:|---:|
| amaze\|raw\|1 | 136 | 4 | 0 |
| amaze\|raw\|2 | 102 | 4 | 0 |
| joplin\|raw\|1 | 67 | 3 | 0 |
| joplin\|raw\|2 | 66 | 3 | 0 |
| lesspass\|raw\|1 | 30 | 2 | 0 |
| lesspass\|raw\|2 | 37 | 11 | 0 |
| markor\|raw\|1 | 68 | 4 | 0 |
| markor\|raw\|2 | 68 | 3 | 0 |
| seal\|raw\|1 | 106 | 2 | 0 |
| seal\|raw\|2 | 112 | 2 | 0 |
| unitto\|raw\|1 | 59 | 2 | 0 |
| unitto\|raw\|2 | 57 | 10 | 0 |

A cell that never typed the method, or that reached for `hd`, measures something other than the arm it is labelled as and must be dropped before any raw ratio is quoted.

### Did the bare arm rederive the method?

3/12 bare runs wrote or ran a tree-dump wrapper of their own, first at command 3-24. Cells: joplin|bare|2 (71), lesspass|bare|1 (4), lesspass|bare|2 (2).

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
  which cover an unmeasured share of each arm's `exec` calls: a command run inside a shell script or a
  loop the agent wrote is one event, so counts are a floor, and they are a lower floor for the
  arm that wrapped its tool.
- Raw data: `runs.json` (cell -> session), `metrics.json`, `tasks.json`, `bypass.json`.
- Dump validity: the preflight `evals/test_dumps.py` reported no `problems` for any of the six
  apps, but several apps' dump commands exited non-zero (the command reads app files that do not
  exist in a freshly installed app). The script does not fail on that, so the playbook's "rc=0
  for every app" condition was NOT strictly met; the per-app trees themselves dumped and the
  final state dumps graded cleanly, so the matrix stands, but this is a weaker preflight than
  the procedure asks for and `test_dumps.py` should be made to exit non-zero on it.

