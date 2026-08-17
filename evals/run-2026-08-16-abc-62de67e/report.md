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
89 screenshots across ~30 tasks. So this mostly measures **the skill vs. visual computer use**, the comparison the plugin README claims — and it is the flattering framing, not the harsh one. Re-check
this split every run before quoting the numbers; it decides which experiment you ran, and it
has flipped between runs of the same matrix.

The opposite failure — completing tasks by writing device state instead of driving the UI
(`adb shell mkdir` for "create a folder") — is counted too: runs touching device state directly,
4/12 hybrid, 4/12 bare, 5/12 raw.
A large imbalance here invalidates the ACU comparison, because one arm is doing less work.

## Headline

| metric | arm | mean | median | cv | p90 | max |
|---|---|---|---|---|---|---|
| ACU | hybrid | 15.9 | 14.6 | 0.38 | 16.6 | 31.3 |
| ACU | bare | 18.7 | 17.6 | 0.32 | 24.9 | 29.9 |
| ACU | raw | 11.8 | 11.2 | 0.26 | 13.6 | 19.1 |
| perception tokens | hybrid | 51,692 | 43,584 | 0.70 | 54,487 | 159,155 |
| perception tokens | bare | 118,248 | 131,590 | 0.64 | 186,776 | 227,236 |
| perception tokens | raw | 21,414 | 20,536 | 0.22 | 25,750 | 28,748 |
| screenshots | hybrid | 12 | 4 | 1.99 | 9 | 86 |
| screenshots | bare | 84 | 89 | 0.46 | 122 | 136 |
| screenshots | raw | 3 | 2 | 0.55 | 5 | 7 |
| tasks done (of ~30) | hybrid | 28.2 | 28.0 | 0.04 | 30.0 | 30.0 |
| tasks done (of ~30) | bare | 27.5 | 28.0 | 0.06 | 28.0 | 30.0 |
| tasks done (of ~30) | raw | 28.2 | 28.5 | 0.05 | 29.0 | 30.0 |

Ratios against bare — ACU: hybrid **0.85x**, raw **0.63x**. Perception tokens:
hybrid **0.44x**, raw **0.18x**. Iterations: hybrid **0.96x**, raw **0.78x**. Exec calls:
hybrid **1.63x**, raw **1.36x**. Tasks done: hybrid **1.03x**, raw **1.02x**.

Worst run by perception tokens — hybrid 159,155 (amaze|hybrid|2), bare 227,236 (markor|bare|1), raw 28,748 (amaze|raw|1).


### ACU by stack

| stack | hybrid mean | cv | bare mean | cv | raw mean | cv | hybrid/bare | raw/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 15.0 | 0.13 | 14.8 | 0.21 | 11.2 | 0.12 | 1.01x | 0.76x |
| rn | 11.7 | 0.25 | 15.7 | 0.25 | 9.5 | 0.21 | 0.74x | 0.61x |
| views | 21.0 | 0.37 | 25.7 | 0.13 | 14.8 | 0.21 | 0.82x | 0.57x |
| **all** | 15.9 | 0.38 | 18.7 | 0.32 | 11.8 | 0.26 | 0.85x | 0.63x |

### Perception tokens by stack

| stack | hybrid mean | cv | bare mean | cv | raw mean | cv | hybrid/bare | raw/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 44,976 | 0.15 | 129,972 | 0.61 | 21,354 | 0.14 | 0.35x | 0.16x |
| rn | 32,386 | 0.36 | 67,282 | 1.04 | 19,113 | 0.33 | 0.48x | 0.28x |
| views | 77,715 | 0.72 | 157,489 | 0.42 | 23,776 | 0.17 | 0.49x | 0.15x |
| **all** | 51,692 | 0.70 | 118,248 | 0.64 | 21,414 | 0.22 | 0.44x | 0.18x |

### Iterations by stack

| stack | hybrid mean | cv | bare mean | cv | raw mean | cv | hybrid/bare | raw/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 172 | 0.17 | 143 | 0.23 | 136 | 0.08 | 1.20x | 0.95x |
| rn | 128 | 0.25 | 160 | 0.25 | 119 | 0.20 | 0.80x | 0.75x |
| views | 227 | 0.37 | 248 | 0.23 | 175 | 0.21 | 0.92x | 0.70x |
| **all** | 176 | 0.37 | 183 | 0.34 | 143 | 0.24 | 0.96x | 0.78x |

### Screenshots by stack

| stack | hybrid mean | cv | bare mean | cv | raw mean | cv | hybrid/bare | raw/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 8 | 0.35 | 78 | 0.67 | 2 | 0.40 | 0.10x | 0.03x |
| rn | 4 | 0.62 | 79 | 0.13 | 4 | 0.61 | 0.05x | 0.05x |
| views | 24 | 1.75 | 94 | 0.50 | 4 | 0.55 | 0.25x | 0.04x |
| **all** | 12 | 1.99 | 84 | 0.46 | 3 | 0.55 | 0.14x | 0.04x |

### Tasks done (of ~30) by stack

| stack | hybrid mean | cv | bare mean | cv | raw mean | cv | hybrid/bare | raw/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 27.0 | 0.00 | 26.5 | 0.09 | 26.8 | 0.05 | 1.02x | 1.01x |
| rn | 28.8 | 0.03 | 28.8 | 0.03 | 28.8 | 0.04 | 1.00x | 1.00x |
| views | 29.0 | 0.04 | 27.2 | 0.04 | 29.0 | 0.03 | 1.06x | 1.06x |
| **all** | 28.2 | 0.04 | 27.5 | 0.06 | 28.2 | 0.05 | 1.03x | 1.02x |

### ACU by app

| app | hybrid mean | cv | bare mean | cv | raw mean | cv | hybrid/bare | raw/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| amaze | 26.9 | 0.23 | 28.1 | 0.09 | 16.7 | 0.21 | 0.95x | 0.59x |
| joplin | 12.5 | 0.24 | 18.8 | 0.12 | 10.3 | 0.12 | 0.66x | 0.55x |
| lesspass | 10.9 | 0.34 | 12.6 | 0.08 | 8.7 | 0.33 | 0.86x | 0.69x |
| markor | 15.1 | 0.13 | 23.3 | 0.10 | 12.9 | 0.08 | 0.65x | 0.55x |
| seal | 16.5 | 0.01 | 14.6 | 0.32 | 11.0 | 0.02 | 1.13x | 0.76x |
| unitto | 13.6 | 0.10 | 15.1 | 0.18 | 11.4 | 0.20 | 0.90x | 0.76x |
| **all** | 15.9 | 0.38 | 18.7 | 0.32 | 11.8 | 0.26 | 0.85x | 0.63x |

### Perception tokens by app

| app | hybrid mean | cv | bare mean | cv | raw mean | cv | hybrid/bare | raw/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| amaze | 112,989 | 0.58 | 129,977 | 0.62 | 24,484 | 0.25 | 0.87x | 0.19x |
| joplin | 38,768 | 0.32 | 69,119 | 1.20 | 22,693 | 0.22 | 0.56x | 0.33x |
| lesspass | 26,002 | 0.38 | 65,444 | 1.34 | 15,534 | 0.41 | 0.40x | 0.24x |
| markor | 42,441 | 0.25 | 185,000 | 0.32 | 23,067 | 0.14 | 0.23x | 0.12x |
| seal | 43,584 | 0.00 | 116,784 | 1.15 | 20,134 | 0.05 | 0.37x | 0.17x |
| unitto | 46,369 | 0.25 | 143,160 | 0.08 | 22,574 | 0.20 | 0.32x | 0.16x |
| **all** | 51,692 | 0.70 | 118,248 | 0.64 | 21,414 | 0.22 | 0.44x | 0.18x |

### Billed input tokens (what ACU tracks)

| | hybrid | bare | raw |
|---|---:|---:|---:|
| billed input, median | 12.33 Mtok | 12.96 Mtok | 9.75 Mtok |
| billed input, mean | 13.45 Mtok | 13.81 Mtok | 10.21 Mtok |
| peak resident context | 115,550 | 101,612 | 105,225 |
| turns | 176 | 183 | 143 |
| perception tokens | 51,692 | 118,248 | 21,414 |

Billed input is the integral of context size over turns, so a token added at turn *i* is charged again at every turn after it. Against bare on the median run: hybrid **0.95x**, raw **0.75x** — a perception ratio does not carry into cost, because a whole run's perception spend is a fraction of a percent of what it bills.

### Where the ACU goes

| per run | hybrid | bare | raw |
|---|---:|---:|---:|
| commands before the first action | 6.17 | 6.92 | 3.33 |
| of those, writing its own tooling | 0.17 | 0.08 | 0.00 |
| looks/task | 4.24 | 1.91 | 2.71 |
| perception tokens per look | 429 | 60,571 | 329 |
| actions per look | 1.19 | 9.78 | 2.11 |
| blind multi-action commands | 6.50 | 18.92 | 22.42 |
| turns/task | 6.26 | 6.71 | 5.09 |
| ACU/turn | 0.0906 | 0.1038 | 0.0824 |
| ACU/task | 0.57 | 0.69 | 0.42 |

Across the 24 hybrid/bare cells, one extra look per task costs **0.035 ACU per task** (0.99 ACU over a 28-task run) — the strongest per-cell predictor of ACU after turn count itself. hybrid takes 4.24 looks per task against bare's 1.91, which alone prices at +2.29 ACU per run against an observed gap of -3.38. The cheaper look is spent on more looking: bootstrapping the improvised tooling is 0.1 commands of a 183-turn run, so there is no setup tax to amortise.

### Which observation verb the hybrid arm typed

| verb | calls | share |
|---|---:|---:|
| `hd see --find` | 389 | 49% |
| `hd see (delta on a re-observation)` | 314 | 39% |
| `hd see -q (capture, print nothing)` | 70 | 9% |
| `hd see --full` | 23 | 3% |

Of the 314 plain `hd see` re-observations, 126 (40%) directly followed a `--find` or `-q` and 4 a `--full`. `--find` and `-q` render the whole tree but print only the matches (or nothing), so this revision keys the diff baseline off the rendering the caller was SHOWN: those re-observations diff against the last tree that actually reached the agent rather than answering `# no change since the last see` about a screen it has never seen. `evals/test_seen_baseline.py` is the regression; re-read this share every run, since it decides how much that behaviour is worth.


### Replacing a value that is already in a field

| | hybrid | bare | raw |
|---|---:|---:|---:|
| hand-rolled deletion loops | 1 | 15 | 17 |
| runs doing it | 1/12 | 5/12 | 7/12 |

Every arm meets the same fields, and none of the three tools had a verb for emptying one, so the agents sent `KEYCODE_MOVE_END` and a guessed number of backspaces. The count is not knowable from outside the tree — the guesses escalate within a run (`seal|hybrid|1`: 20, 30, 10, 30, 30, 40, 20, 40, 20) and a low one leaves the tail of the old value fused to the new text. `hd type "x" -r` takes the count from the focused node's own text; `evals/test_replace.py` prices it against the guess.

### Finding the focused field

| | hybrid | bare | raw |
|---|---:|---:|---:|
| focus-hunting commands | 91 | 30 | 34 |
| runs doing it | 10/12 | 8/12 | 9/12 |

The hybrid arm spent 91 commands in 10/12 runs answering a question its own tree already knew the answer to: `hd see --full | grep -i edit`, `hd see --find EditText`, `keyevent 123`. 47 of them are in the compose cells — the stack where hybrid's perception tokens run furthest above bare. `parse()` already read `focused` off every node; `render()` printed every other state but that one, so the precondition of the three text verbs was the one fact a look could not answer.

### Looks bought to turn a label into an index

| | hybrid | bare | raw |
|---|---:|---:|---:|
| look-only commands | 333 | 0 | 0 |
| ...followed by nothing but an index tap | 82 | 0 | 0 |
| runs doing it | 10/12 | 0/12 | 0/12 |
| actions taken by selector/label | 200 | 1 | 0 |

82 of the hybrid arm's 333 look-only commands, in 10/12 runs, were followed by nothing but `hd tap <index>` — a turn spent numbering a target the agent could already name. The other arms never pay it, because they tap coordinates the tree already printed and never index anything. `hd tap "PAT"` is hd's form of acting by name and was typed on 200 of the hybrid arm's 657 taps (30%) — documented but under-typed, so hd names it itself after a look that bought nothing but an index (`evals/test_tap_hint.py`; `evals/test_tap_label.py` prices the verb).


### Did the raw arm use the method it was handed?

12/12 raw runs drove the emulator with the wrapper (`python3 ~/ui.py see`, `uiautomator dump`), 849 invocations in total, first used at command 2-10 of the run. 0/12 runs invoked `hd` (contamination).

| cell | wrapper invocations | first at command | `hd` invocations |
|---|---:|---:|---:|
| amaze\|raw\|1 | 130 | 3 | 0 |
| amaze\|raw\|2 | 112 | 3 | 0 |
| joplin\|raw\|1 | 64 | 5 | 0 |
| joplin\|raw\|2 | 63 | 3 | 0 |
| lesspass\|raw\|1 | 26 | 6 | 0 |
| lesspass\|raw\|2 | 23 | 2 | 0 |
| markor\|raw\|1 | 77 | 6 | 0 |
| markor\|raw\|2 | 36 | 5 | 0 |
| seal\|raw\|1 | 97 | 2 | 0 |
| seal\|raw\|2 | 103 | 3 | 0 |
| unitto\|raw\|1 | 65 | 8 | 0 |
| unitto\|raw\|2 | 53 | 10 | 0 |

A cell that never typed the method, or that reached for `hd`, measures something other than the arm it is labelled as and must be dropped before any raw ratio is quoted.

### Did the bare arm rederive the method?

2/12 bare runs wrote or ran a tree-dump wrapper of their own, first at command 3-5. Cells: amaze|bare|1 (1), seal|bare|1 (74).

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

