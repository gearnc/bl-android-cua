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
improvised tree tooling, 9/12 did visual CUA,
2 sat in between. Median bare run:
84 screenshots across ~30 tasks. So this mostly measures **the skill vs. visual computer use**, the comparison the plugin README claims — and it is the flattering framing, not the harsh one. Re-check
this split every run before quoting the numbers; it decides which experiment you ran, and it
has flipped between runs of the same matrix.

The opposite failure — completing tasks by writing device state instead of driving the UI
(`adb shell mkdir` for "create a folder") — is counted too: runs touching device state directly,
5/12 hybrid, 3/12 bare, 6/12 raw.
A large imbalance here invalidates the ACU comparison, because one arm is doing less work.

## Headline

| metric | arm | mean | median | cv | p90 | max |
|---|---|---|---|---|---|---|
| ACU | hybrid | 15.9 | 15.0 | 0.38 | 17.6 | 28.0 |
| ACU | bare | 18.2 | 16.9 | 0.27 | 22.9 | 27.3 |
| ACU | raw | 11.1 | 11.1 | 0.33 | 14.3 | 17.8 |
| perception tokens | hybrid | 41,814 | 40,988 | 0.38 | 50,336 | 71,047 |
| perception tokens | bare | 118,708 | 127,098 | 0.66 | 179,010 | 264,353 |
| perception tokens | raw | 20,007 | 22,192 | 0.27 | 22,917 | 25,966 |
| screenshots | hybrid | 5 | 4 | 0.62 | 7 | 10 |
| screenshots | bare | 77 | 84 | 0.64 | 118 | 160 |
| screenshots | raw | 3 | 2 | 0.61 | 4 | 6 |
| tasks done (of ~30) | hybrid | 27.9 | 28.5 | 0.06 | 29.0 | 30.0 |
| tasks done (of ~30) | bare | 28.2 | 28.5 | 0.06 | 29.0 | 30.0 |
| tasks done (of ~30) | raw | 28.2 | 28.5 | 0.05 | 29.0 | 30.0 |

Ratios against bare — ACU: hybrid **0.87x**, raw **0.61x**. Perception tokens:
hybrid **0.35x**, raw **0.17x**. Iterations: hybrid **0.94x**, raw **0.69x**. Exec calls:
hybrid **1.55x**, raw **1.14x**. Tasks done: hybrid **0.99x**, raw **1.00x**.

Worst run by perception tokens — hybrid 71,047 (amaze|hybrid|2), bare 264,353 (amaze|bare|2), raw 25,966 (joplin|raw|1).


### ACU by stack

| stack | hybrid mean | cv | bare mean | cv | raw mean | cv | hybrid/bare | raw/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 13.5 | 0.15 | 19.5 | 0.25 | 11.5 | 0.10 | 0.69x | 0.59x |
| rn | 11.8 | 0.29 | 14.7 | 0.19 | 7.4 | 0.38 | 0.80x | 0.50x |
| views | 22.3 | 0.27 | 20.3 | 0.29 | 14.4 | 0.20 | 1.10x | 0.71x |
| **all** | 15.9 | 0.38 | 18.2 | 0.27 | 11.1 | 0.33 | 0.87x | 0.61x |

### Perception tokens by stack

| stack | hybrid mean | cv | bare mean | cv | raw mean | cv | hybrid/bare | raw/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 38,229 | 0.23 | 165,716 | 0.14 | 21,596 | 0.08 | 0.23x | 0.13x |
| rn | 29,828 | 0.42 | 67,202 | 0.88 | 15,858 | 0.52 | 0.44x | 0.24x |
| views | 57,385 | 0.21 | 123,206 | 0.88 | 22,568 | 0.03 | 0.47x | 0.18x |
| **all** | 41,814 | 0.38 | 118,708 | 0.66 | 20,007 | 0.27 | 0.35x | 0.17x |

### Iterations by stack

| stack | hybrid mean | cv | bare mean | cv | raw mean | cv | hybrid/bare | raw/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 149 | 0.18 | 196 | 0.32 | 139 | 0.11 | 0.76x | 0.71x |
| rn | 132 | 0.30 | 160 | 0.23 | 90 | 0.39 | 0.82x | 0.57x |
| views | 243 | 0.27 | 204 | 0.15 | 159 | 0.20 | 1.19x | 0.78x |
| **all** | 175 | 0.38 | 187 | 0.24 | 130 | 0.31 | 0.94x | 0.69x |

### Screenshots by stack

| stack | hybrid mean | cv | bare mean | cv | raw mean | cv | hybrid/bare | raw/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 6 | 0.39 | 107 | 0.14 | 4 | 0.37 | 0.05x | 0.03x |
| rn | 4 | 0.91 | 56 | 0.61 | 2 | 0.95 | 0.08x | 0.04x |
| views | 4 | 0.74 | 67 | 1.13 | 2 | 0.41 | 0.06x | 0.03x |
| **all** | 5 | 0.62 | 77 | 0.64 | 3 | 0.61 | 0.06x | 0.03x |

### Tasks done (of ~30) by stack

| stack | hybrid mean | cv | bare mean | cv | raw mean | cv | hybrid/bare | raw/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 26.2 | 0.08 | 26.5 | 0.07 | 26.8 | 0.05 | 0.99x | 1.01x |
| rn | 28.5 | 0.02 | 29.5 | 0.02 | 29.0 | 0.03 | 0.97x | 0.98x |
| views | 29.0 | 0.03 | 28.5 | 0.02 | 28.8 | 0.02 | 1.02x | 1.01x |
| **all** | 27.9 | 0.06 | 28.2 | 0.06 | 28.2 | 0.05 | 0.99x | 1.00x |

### ACU by app

| app | hybrid mean | cv | bare mean | cv | raw mean | cv | hybrid/bare | raw/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| amaze | 27.5 | 0.03 | 22.9 | 0.27 | 16.3 | 0.13 | 1.20x | 0.71x |
| joplin | 14.6 | 0.12 | 16.8 | 0.10 | 9.7 | 0.15 | 0.87x | 0.58x |
| lesspass | 9.0 | 0.06 | 12.7 | 0.16 | 5.1 | 0.03 | 0.71x | 0.40x |
| markor | 17.2 | 0.03 | 17.7 | 0.35 | 12.6 | 0.19 | 0.97x | 0.71x |
| seal | 15.1 | 0.10 | 23.7 | 0.05 | 12.4 | 0.06 | 0.64x | 0.52x |
| unitto | 11.9 | 0.01 | 15.4 | 0.05 | 10.7 | 0.09 | 0.78x | 0.69x |
| **all** | 15.9 | 0.38 | 18.2 | 0.27 | 11.1 | 0.33 | 0.87x | 0.61x |

### Perception tokens by app

| app | hybrid mean | cv | bare mean | cv | raw mean | cv | hybrid/bare | raw/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| amaze | 67,118 | 0.08 | 156,108 | 0.98 | 22,230 | 0.03 | 0.43x | 0.14x |
| joplin | 40,590 | 0.00 | 117,692 | 0.07 | 22,558 | 0.21 | 0.34x | 0.19x |
| lesspass | 19,066 | 0.03 | 16,712 | 0.86 | 9,157 | 0.02 | 1.14x | 0.55x |
| markor | 47,652 | 0.08 | 90,304 | 0.98 | 22,906 | 0.04 | 0.53x | 0.25x |
| seal | 41,524 | 0.26 | 179,075 | 0.00 | 20,628 | 0.11 | 0.23x | 0.12x |
| unitto | 34,935 | 0.26 | 152,357 | 0.20 | 22,564 | 0.02 | 0.23x | 0.15x |
| **all** | 41,814 | 0.38 | 118,708 | 0.66 | 20,007 | 0.27 | 0.35x | 0.17x |

### Billed input tokens (what ACU tracks)

| | hybrid | bare | raw |
|---|---:|---:|---:|
| billed input, median | 13.16 Mtok | 12.71 Mtok | 9.21 Mtok |
| billed input, mean | 13.88 Mtok | 13.57 Mtok | 9.16 Mtok |
| peak resident context | 118,479 | 100,723 | 103,599 |
| turns | 175 | 187 | 130 |
| perception tokens | 41,814 | 118,708 | 20,007 |

Billed input is the integral of context size over turns, so a token added at turn *i* is charged again at every turn after it. Against bare on the median run: hybrid **1.04x**, raw **0.72x** — a perception ratio does not carry into cost, because a whole run's perception spend is a fraction of a percent of what it bills.

### Where the ACU goes

| per run | hybrid | bare | raw |
|---|---:|---:|---:|
| commands before the first action | 7.08 | 14.50 | 3.58 |
| of those, writing its own tooling | 0.00 | 0.33 | 0.00 |
| looks/task | 4.32 | 2.19 | 2.73 |
| perception tokens per look | 348 | 37,723 | 288 |
| actions per look | 1.40 | 5.78 | 1.96 |
| blind multi-action commands | 8.58 | 15.50 | 20.25 |
| turns/task | 6.26 | 6.71 | 4.63 |
| ACU/turn | 0.0910 | 0.0980 | 0.0852 |
| ACU/task | 0.57 | 0.65 | 0.40 |

Across the 24 hybrid/bare cells, one extra look per task costs **0.043 ACU per task** (1.20 ACU over a 28-task run) — the strongest per-cell predictor of ACU after turn count itself. hybrid takes 4.32 looks per task against bare's 2.19, which alone prices at +2.56 ACU per run against an observed gap of -2.39. The cheaper look is spent on more looking: bootstrapping the improvised tooling is 0.3 commands of a 187-turn run, so there is no setup tax to amortise.

### Which observation verb the hybrid arm typed

| verb | calls | share |
|---|---:|---:|
| `hd see (delta on a re-observation)` | 384 | 46% |
| `hd see --find` | 360 | 43% |
| `hd see -q (capture, print nothing)` | 50 | 6% |
| `hd see --full` | 40 | 5% |

Of the 384 plain `hd see` re-observations, 131 (34%) directly followed a `--find` or `-q` and 15 a `--full`. `--find` and `-q` render the whole tree but print only the matches (or nothing), so this revision keys the diff baseline off the rendering the caller was SHOWN: those re-observations diff against the last tree that actually reached the agent rather than answering `# no change since the last see` about a screen it has never seen. `evals/test_seen_baseline.py` is the regression; re-read this share every run, since it decides how much that behaviour is worth.


### Replacing a value that is already in a field

| | hybrid | bare | raw |
|---|---:|---:|---:|
| hand-rolled deletion loops | 4 | 11 | 18 |
| runs doing it | 3/12 | 7/12 | 9/12 |

Every arm meets the same fields, and none of the three tools had a verb for emptying one, so the agents sent `KEYCODE_MOVE_END` and a guessed number of backspaces. The count is not knowable from outside the tree — the guesses escalate within a run (`seal|hybrid|1`: 20, 30, 10, 30, 30, 40, 20, 40, 20) and a low one leaves the tail of the old value fused to the new text. `hd type "x" -r` takes the count from the focused node's own text; `evals/test_replace.py` prices it against the guess.

### Finding the focused field

| | hybrid | bare | raw |
|---|---:|---:|---:|
| focus-hunting commands | 79 | 20 | 38 |
| runs doing it | 11/12 | 7/12 | 11/12 |

The hybrid arm spent 79 commands in 11/12 runs answering a question its own tree already knew the answer to: `hd see --full | grep -i edit`, `hd see --find EditText`, `keyevent 123`. 50 of them are in the compose cells — the stack where hybrid's perception tokens run furthest above bare. `parse()` already read `focused` off every node; `render()` printed every other state but that one, so the precondition of the three text verbs was the one fact a look could not answer.

### Looks bought to turn a label into an index

| | hybrid | bare | raw |
|---|---:|---:|---:|
| look-only commands | 305 | 0 | 0 |
| ...followed by nothing but an index tap | 106 | 0 | 0 |
| runs doing it | 12/12 | 0/12 | 0/12 |
| actions taken by selector/label | 214 | 0 | 0 |

106 of the hybrid arm's 305 look-only commands, in 12/12 runs, were followed by nothing but `hd tap <index>` — a turn spent numbering a target the agent could already name. The other arms never pay it, because they tap coordinates the tree already printed and never index anything. `hd tap "PAT"` is hd's form of acting by name and was typed on 214 of the hybrid arm's 806 taps (27%) — documented but under-typed, so hd names it itself after a look that bought nothing but an index (`evals/test_tap_hint.py`; `evals/test_tap_label.py` prices the verb).

### Turns spent hunting a row below the fold

| | hybrid | bare | raw |
|---|---:|---:|---:|
| multi-swipe hunts | 24 | 18 | 13 |
| commands inside them | 72 | 81 | 38 |
| runs doing it | 10/12 | 8/12 | 8/12 |

The hybrid arm spent 72 commands inside 24 swipe-then-look hunts across 10/12 of its runs. Every look in one of them answers nothing but “did the row arrive yet?”, so `hd swipe <dir> --until PAT` runs the loop inside one process — swipe, re-cache silently, print only the lines that answer — and stops early at the end of the list (`evals/bench_scroll_hunt.py`).


### Did the raw arm use the method it was handed?

12/12 raw runs drove the emulator with the wrapper (`python3 ~/ui.py see`, `uiautomator dump`), 865 invocations in total, first used at command 2-12 of the run. 0/12 runs invoked `hd` (contamination).

| cell | wrapper invocations | first at command | `hd` invocations |
|---|---:|---:|---:|
| amaze\|raw\|1 | 97 | 3 | 0 |
| amaze\|raw\|2 | 109 | 6 | 0 |
| joplin\|raw\|1 | 69 | 2 | 0 |
| joplin\|raw\|2 | 69 | 2 | 0 |
| lesspass\|raw\|1 | 22 | 7 | 0 |
| lesspass\|raw\|2 | 17 | 6 | 0 |
| markor\|raw\|1 | 67 | 4 | 0 |
| markor\|raw\|2 | 63 | 4 | 0 |
| seal\|raw\|1 | 104 | 2 | 0 |
| seal\|raw\|2 | 105 | 2 | 0 |
| unitto\|raw\|1 | 79 | 12 | 0 |
| unitto\|raw\|2 | 64 | 10 | 0 |

A cell that never typed the method, or that reached for `hd`, measures something other than the arm it is labelled as and must be dropped before any raw ratio is quoted.

### Did the bare arm rederive the method?

3/12 bare runs wrote or ran a tree-dump wrapper of their own, first at command 3-4. Cells: amaze|bare|1 (125), lesspass|bare|1 (7), markor|bare|1 (85).

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
- Dump validity: `python3 evals/test_dumps.py markor amaze seal unitto joplin lesspass` returned
  rc=0 with no `problems` for all six apps in the matrix, with each app launched first — a dump
  that reads an app's files exits non-zero until the app has run once. Whole-suite runs of the
  script still fail on apps outside this matrix, which is not a condition on this run.

