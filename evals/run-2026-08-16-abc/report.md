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
<= 5 screenshots and as *visual CUA* at >= 20: 1/12 bare runs
improvised tree tooling, 11/12 did visual CUA,
0 sat in between. Median bare run:
100 screenshots across ~30 tasks. So this mostly measures **the skill vs. visual computer use**, the comparison the plugin README claims — and it is the flattering framing, not the harsh one. Re-check
this split every run before quoting the numbers; it decides which experiment you ran, and it
has flipped between runs of the same matrix.

The opposite failure — completing tasks by writing device state instead of driving the UI
(`adb shell mkdir` for "create a folder") — is counted too: runs touching device state directly,
5/12 hybrid, 4/12 bare, 6/12 raw.
A large imbalance here invalidates the ACU comparison, because one arm is doing less work.

## Headline

| metric | arm | mean | median | cv | p90 | max |
|---|---|---|---|---|---|---|
| ACU | hybrid | 15.4 | 14.5 | 0.33 | 19.6 | 25.6 |
| ACU | bare | 19.1 | 19.2 | 0.34 | 25.6 | 29.2 |
| ACU | raw | 12.0 | 11.3 | 0.48 | 15.9 | 24.9 |
| perception tokens | hybrid | 43,990 | 37,138 | 0.42 | 62,359 | 82,962 |
| perception tokens | bare | 126,910 | 128,268 | 0.56 | 189,462 | 242,513 |
| perception tokens | raw | 19,655 | 21,798 | 0.31 | 23,602 | 29,651 |
| screenshots | hybrid | 4 | 4 | 0.46 | 6 | 8 |
| screenshots | bare | 88 | 100 | 0.47 | 115 | 147 |
| screenshots | raw | 3 | 2 | 0.58 | 3 | 7 |
| tasks done (of ~30) | hybrid | 28.0 | 28.5 | 0.06 | 29.0 | 30.0 |
| tasks done (of ~30) | bare | 28.2 | 28.5 | 0.06 | 30.0 | 30.0 |
| tasks done (of ~30) | raw | 28.2 | 28.0 | 0.03 | 29.0 | 30.0 |

Ratios against bare — ACU: hybrid **0.81x**, raw **0.63x**. Perception tokens:
hybrid **0.35x**, raw **0.15x**. Iterations: hybrid **0.94x**, raw **0.81x**. Exec calls:
hybrid **1.86x**, raw **1.59x**. Tasks done: hybrid **0.99x**, raw **1.00x**.

Worst run by perception tokens — hybrid 82,962 (amaze|hybrid|2), bare 242,513 (amaze|bare|1), raw 29,651 (markor|raw|2).


### ACU by stack

| stack | hybrid mean | cv | bare mean | cv | raw mean | cv | hybrid/bare | raw/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 13.9 | 0.15 | 17.2 | 0.19 | 10.8 | 0.13 | 0.81x | 0.62x |
| rn | 10.8 | 0.20 | 14.3 | 0.43 | 7.0 | 0.42 | 0.76x | 0.49x |
| views | 21.4 | 0.14 | 25.6 | 0.16 | 18.2 | 0.26 | 0.84x | 0.71x |
| **all** | 15.4 | 0.33 | 19.1 | 0.34 | 12.0 | 0.48 | 0.81x | 0.63x |

### Perception tokens by stack

| stack | hybrid mean | cv | bare mean | cv | raw mean | cv | hybrid/bare | raw/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 38,089 | 0.22 | 165,551 | 0.24 | 20,191 | 0.17 | 0.23x | 0.12x |
| rn | 29,844 | 0.28 | 97,538 | 0.71 | 13,897 | 0.40 | 0.31x | 0.14x |
| views | 64,038 | 0.25 | 117,640 | 0.81 | 24,876 | 0.13 | 0.54x | 0.21x |
| **all** | 43,990 | 0.42 | 126,910 | 0.56 | 19,655 | 0.31 | 0.35x | 0.15x |

### Iterations by stack

| stack | hybrid mean | cv | bare mean | cv | raw mean | cv | hybrid/bare | raw/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 151 | 0.17 | 162 | 0.29 | 134 | 0.12 | 0.93x | 0.82x |
| rn | 114 | 0.20 | 134 | 0.33 | 87 | 0.41 | 0.85x | 0.65x |
| views | 234 | 0.14 | 234 | 0.19 | 208 | 0.30 | 1.00x | 0.89x |
| **all** | 166 | 0.35 | 176 | 0.34 | 143 | 0.45 | 0.94x | 0.81x |

### Screenshots by stack

| stack | hybrid mean | cv | bare mean | cv | raw mean | cv | hybrid/bare | raw/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 4 | 0.43 | 104 | 0.21 | 3 | 0.81 | 0.04x | 0.03x |
| rn | 3 | 0.27 | 70 | 0.72 | 2 | 0.41 | 0.04x | 0.03x |
| views | 5 | 0.53 | 91 | 0.56 | 3 | 0.27 | 0.05x | 0.03x |
| **all** | 4 | 0.46 | 88 | 0.47 | 3 | 0.58 | 0.05x | 0.03x |

### Tasks done (of ~30) by stack

| stack | hybrid mean | cv | bare mean | cv | raw mean | cv | hybrid/bare | raw/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 27.0 | 0.09 | 27.2 | 0.08 | 27.2 | 0.02 | 0.99x | 1.00x |
| rn | 29.2 | 0.02 | 29.2 | 0.03 | 28.8 | 0.02 | 1.00x | 0.98x |
| views | 27.8 | 0.02 | 28.0 | 0.05 | 28.8 | 0.03 | 0.99x | 1.03x |
| **all** | 28.0 | 0.06 | 28.2 | 0.06 | 28.2 | 0.03 | 0.99x | 1.00x |

### ACU by app

| app | hybrid mean | cv | bare mean | cv | raw mean | cv | hybrid/bare | raw/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| amaze | 23.6 | 0.12 | 26.6 | 0.05 | 16.9 | 0.08 | 0.89x | 0.63x |
| joplin | 12.5 | 0.06 | 19.2 | 0.02 | 9.4 | 0.18 | 0.65x | 0.49x |
| lesspass | 9.1 | 0.15 | 9.4 | 0.46 | 4.6 | 0.06 | 0.97x | 0.49x |
| markor | 19.3 | 0.02 | 24.6 | 0.26 | 19.6 | 0.38 | 0.78x | 0.80x |
| seal | 15.1 | 0.07 | 19.8 | 0.10 | 11.4 | 0.04 | 0.76x | 0.57x |
| unitto | 12.8 | 0.20 | 14.7 | 0.12 | 10.2 | 0.21 | 0.87x | 0.69x |
| **all** | 15.4 | 0.33 | 19.1 | 0.34 | 12.0 | 0.48 | 0.81x | 0.63x |

### Perception tokens by app

| app | hybrid mean | cv | bare mean | cv | raw mean | cv | hybrid/bare | raw/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| amaze | 74,650 | 0.16 | 157,559 | 0.76 | 23,258 | 0.05 | 0.47x | 0.15x |
| joplin | 37,138 | 0.03 | 132,374 | 0.61 | 18,280 | 0.23 | 0.28x | 0.14x |
| lesspass | 22,548 | 0.05 | 62,702 | 0.88 | 9,514 | 0.05 | 0.36x | 0.15x |
| markor | 53,424 | 0.24 | 77,721 | 1.04 | 26,494 | 0.17 | 0.69x | 0.34x |
| seal | 33,497 | 0.07 | 188,039 | 0.23 | 20,034 | 0.18 | 0.18x | 0.11x |
| unitto | 42,682 | 0.25 | 143,062 | 0.21 | 20,348 | 0.23 | 0.30x | 0.14x |
| **all** | 43,990 | 0.42 | 126,910 | 0.56 | 19,655 | 0.31 | 0.35x | 0.15x |

### Billed input tokens (what ACU tracks)

| | hybrid | bare | raw |
|---|---:|---:|---:|
| billed input, median | 12.34 Mtok | 13.02 Mtok | 9.55 Mtok |
| billed input, mean | 13.19 Mtok | 13.58 Mtok | 10.21 Mtok |
| peak resident context | 121,561 | 101,902 | 102,010 |
| turns | 166 | 176 | 143 |
| perception tokens | 43,990 | 126,910 | 19,655 |

Billed input is the integral of context size over turns, so a token added at turn *i* is charged again at every turn after it. Against bare on the median run: hybrid **0.95x**, raw **0.73x** — a perception ratio does not carry into cost, because a whole run's perception spend is a fraction of a percent of what it bills.

### Where the ACU goes

| per run | hybrid | bare | raw |
|---|---:|---:|---:|
| commands before the first action | 7.42 | 4.17 | 4.42 |
| of those, writing its own tooling | 0.25 | 0.25 | 0.08 |
| looks/task | 2.93 | 1.06 | 2.44 |
| perception tokens per look | 583 | 77,321 | 337 |
| actions per look | 1.81 | 11.43 | 2.07 |
| blind multi-action commands | 11.58 | 15.42 | 21.25 |
| turns/task | 5.99 | 6.35 | 5.06 |
| ACU/turn | 0.0931 | 0.1081 | 0.0830 |
| ACU/task | 0.55 | 0.69 | 0.42 |

Across the 24 hybrid/bare cells, one extra look per task costs **0.046 ACU per task** (1.29 ACU over a 28-task run) — the strongest per-cell predictor of ACU after turn count itself. hybrid takes 2.93 looks per task against bare's 1.06, which alone prices at +2.40 ACU per run against an observed gap of -3.68. The cheaper look is spent on more looking: bootstrapping the improvised tooling is 0.2 commands of a 176-turn run, so there is no setup tax to amortise.

### Which observation verb the hybrid arm typed

| verb | calls | share |
|---|---:|---:|
| `hd see --find` | 466 | 50% |
| `hd see (delta on a re-observation)` | 377 | 41% |
| `hd see --full` | 55 | 6% |
| `hd see -q (capture, print nothing)` | 28 | 3% |

Of the 377 plain `hd see` re-observations, 142 (38%) directly followed a `--find` or `-q` and 9 a `--full`. `--find` and `-q` render the whole tree but print only the matches (or nothing), so this revision keys the diff baseline off the rendering the caller was SHOWN: those re-observations diff against the last tree that actually reached the agent rather than answering `# no change since the last see` about a screen it has never seen. `evals/test_seen_baseline.py` is the regression; re-read this share every run, since it decides how much that behaviour is worth.

### What a plain `hd see` printed

| outcome | count | share |
|---|---:|---:|
| whole tree (`screen changed too much to diff`) | 413 | 68% |
| delta | 194 | 32% |

Counted over every delta-capable look — the 422 plain `hd see` commands above plus the look each action folds in, which is why the total exceeds the command count. The delta is the reason a re-observation is cheap, and it was discarded 68% of the time. Worst cells: amaze|hybrid|2 (63 whole / 5 delta), markor|hybrid|1 (61 whole / 33 delta), amaze|hybrid|1 (57 whole / 13 delta).

Mechanism, measured on the emulator against the revision under test: the delta already reports a scrolled row as one `~ [was]->[now] (x,y)` line, but it re-prints every REMOVED node in full — class, id, flags, coordinates — to say it is gone. Closing Amaze's drawer removes 28 nodes and changes nothing else, and cost 2,482 characters of delta against a 2,313-character tree, so `see` correctly discarded the delta and printed the whole tree: the expensive outcome, reached by describing lines the caller was already holding. The same walk pays it again on the way in, where inserting rows renumbers 39 unmoved nodes into 39 separate `~` lines. Naming a removal by the index the caller read it under (`- [12] "Sort by"`) and collapsing a contiguous constant-shift renumbering into one `~ [a-b]->[c-d]` line cuts that drawer re-observation 2,482 -> 310 characters. `evals/bench_delta_shape.py` is the bench: 18% fewer characters per re-observation over markor/amaze/seal's menu and drawer cases, whole-tree fallbacks 9/18 -> 8/18, with the screen-turnover fallback intact and every printed index checked against the tree the caller actually read.

### Replacing a value that is already in a field

| | hybrid | bare | raw |
|---|---:|---:|---:|
| hand-rolled deletion loops | 3 | 11 | 9 |
| runs doing it | 2/12 | 5/12 | 5/12 |

Every arm meets the same fields, and none of the three tools had a verb for emptying one, so the agents sent `KEYCODE_MOVE_END` and a guessed number of backspaces. The count is not knowable from outside the tree — the guesses escalate within a run (`seal|hybrid|1`: 20, 30, 10, 30, 30, 40, 20, 40, 20) and a low one leaves the tail of the old value fused to the new text. `hd type "x" -r` takes the count from the focused node's own text; `evals/test_replace.py` prices it against the guess.

### Finding the focused field

| | hybrid | bare | raw |
|---|---:|---:|---:|
| focus-hunting commands | 73 | 18 | 38 |
| runs doing it | 11/12 | 8/12 | 11/12 |

The hybrid arm spent 73 commands in 11/12 runs answering a question its own tree already knew the answer to: `hd see --full | grep -i edit`, `hd see --find EditText`, `keyevent 123`. 39 of them are in the compose cells — the stack where hybrid's perception tokens run furthest above bare. `parse()` already read `focused` off every node; `render()` printed every other state but that one, so the precondition of the three text verbs was the one fact a look could not answer.

### Looks bought to turn a label into an index

| | hybrid | bare | raw |
|---|---:|---:|---:|
| look-only commands | 311 | 0 | 0 |
| ...followed by nothing but an index tap | 92 | 0 | 0 |
| runs doing it | 12/12 | 0/12 | 0/12 |
| actions taken by selector/label | 169 | 0 | 0 |

92 of the hybrid arm's 311 look-only commands, in 12/12 runs, were followed by nothing but `hd tap <index>` — a turn spent numbering a target the agent could already name. The other arms never pay it, because they tap coordinates the tree already printed and never index anything. `hd tap "PAT"` is hd's form of acting by name and was typed on 169 of the hybrid arm's 750 taps (23%) — documented but under-typed, so hd names it itself after a look that bought nothing but an index (`evals/test_tap_hint.py`; `evals/test_tap_label.py` prices the verb).


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

3/12 bare runs wrote or ran a tree-dump wrapper of their own, first at command 2-71. Cells: amaze|bare|2 (21), lesspass|bare|1 (1), unitto|bare|2 (5).

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

