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
improvised tree tooling, 3/12 did visual CUA,
7 sat in between. Median bare run:
14 screenshots across ~30 tasks. So this mostly measures **the skill vs. visual computer use**, the comparison the plugin README claims — and it is the flattering framing, not the harsh one. Re-check
this split every run before quoting the numbers; it decides which experiment you ran, and it
has flipped between runs of the same matrix.

The opposite failure — completing tasks by writing device state instead of driving the UI
(`adb shell mkdir` for "create a folder") — is counted too: runs touching device state directly,
6/12 hybrid, 5/12 bare, 7/12 acli.
A large imbalance here invalidates the ACU comparison, because one arm is doing less work.

## Headline

| metric | arm | mean | median | cv | p90 | max |
|---|---|---|---|---|---|---|
| ACU | hybrid | 14.9 | 15.0 | 0.39 | 17.8 | 26.7 |
| ACU | bare | 13.2 | 13.4 | 0.38 | 18.7 | 20.1 |
| ACU | acli | 16.7 | 14.7 | 0.47 | 22.1 | 33.3 |
| perception tokens | hybrid | 44,265 | 45,308 | 0.33 | 53,732 | 73,376 |
| perception tokens | bare | 38,740 | 36,196 | 0.47 | 60,036 | 65,846 |
| perception tokens | acli | 52,838 | 41,252 | 0.59 | 70,497 | 136,646 |
| screenshots | hybrid | 7.0 | 6.0 | 0.66 | 12.0 | 16.0 |
| screenshots | bare | 19.8 | 14.5 | 1.23 | 23.0 | 94.0 |
| screenshots | acli | 20.0 | 14.5 | 1.07 | 31.0 | 81.0 |
| tasks done (of ~30) | hybrid | 27.6 | 28.0 | 0.04 | 29.0 | 29.0 |
| tasks done (of ~30) | bare | 28.0 | 28.0 | 0.04 | 29.0 | 30.0 |
| tasks done (of ~30) | acli | 28.0 | 28.0 | 0.06 | 29.0 | 30.0 |

Ratios against bare — ACU: hybrid **1.13x**, acli **1.27x**. Perception tokens:
hybrid **1.14x**, acli **1.36x**. Iterations: hybrid **1.13x**, acli **1.20x**. Exec calls:
hybrid **1.18x**, acli **1.15x**. Tasks done: hybrid **0.99x**, acli **1.00x**.

Worst run by perception tokens — hybrid 73,376 (amaze|hybrid|1), bare 65,846 (amaze|bare|1), acli 136,646 (markor|acli|1).


### ACU by stack

| stack | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 14.0 | 0.27 | 11.4 | 0.30 | 10.9 | 0.18 | 1.23x | 0.96x |
| rn | 10.9 | 0.48 | 11.2 | 0.59 | 14.8 | 0.40 | 0.97x | 1.32x |
| views | 19.8 | 0.26 | 16.9 | 0.17 | 24.4 | 0.30 | 1.17x | 1.44x |
| **all** | 14.9 | 0.39 | 13.2 | 0.38 | 16.7 | 0.47 | 1.13x | 1.27x |

### Perception tokens by stack

| stack | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 42,231 | 0.09 | 48,220 | 0.29 | 33,620 | 0.22 | 0.88x | 0.70x |
| rn | 35,040 | 0.50 | 23,072 | 0.65 | 51,444 | 0.38 | 1.52x | 2.23x |
| views | 55,525 | 0.22 | 44,929 | 0.39 | 73,448 | 0.62 | 1.24x | 1.63x |
| **all** | 44,265 | 0.33 | 38,740 | 0.47 | 52,838 | 0.59 | 1.14x | 1.36x |

### Iterations by stack

| stack | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 168 | 0.25 | 143 | 0.24 | 135 | 0.13 | 1.18x | 0.95x |
| rn | 138 | 0.43 | 130 | 0.52 | 175 | 0.31 | 1.06x | 1.34x |
| views | 240 | 0.27 | 208 | 0.21 | 268 | 0.26 | 1.15x | 1.29x |
| **all** | 182 | 0.37 | 160 | 0.36 | 193 | 0.39 | 1.13x | 1.20x |

### Screenshots by stack

| stack | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 8.2 | 0.66 | 19.5 | 0.25 | 8.0 | 0.60 | 0.42x | 0.41x |
| rn | 7.8 | 0.64 | 29.8 | 1.45 | 22.0 | 0.60 | 0.26x | 0.74x |
| views | 5.0 | 0.78 | 10.0 | 0.50 | 30.0 | 1.14 | 0.50x | 3.00x |
| **all** | 7.0 | 0.66 | 19.8 | 1.23 | 20.0 | 1.07 | 0.35x | 1.01x |

### Tasks done (of ~30) by stack

| stack | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| compose | 27.0 | 0.07 | 27.0 | 0.03 | 26.5 | 0.09 | 1.00x | 0.98x |
| rn | 28.0 | 0.04 | 28.8 | 0.03 | 29.2 | 0.02 | 0.97x | 1.02x |
| views | 27.8 | 0.02 | 28.2 | 0.04 | 28.2 | 0.02 | 0.98x | 1.00x |
| **all** | 27.6 | 0.04 | 28.0 | 0.04 | 28.0 | 0.06 | 0.99x | 1.00x |

### ACU by app

| app | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| amaze | 23.5 | 0.20 | 19.2 | 0.04 | 26.6 | 0.36 | 1.22x | 1.39x |
| joplin | 15.5 | 0.05 | 16.3 | 0.33 | 14.5 | 0.17 | 0.95x | 0.89x |
| lesspass | 6.4 | 0.12 | 6.2 | 0.06 | 15.1 | 0.66 | 1.03x | 2.43x |
| markor | 16.1 | 0.12 | 14.6 | 0.12 | 22.1 | 0.33 | 1.11x | 1.52x |
| seal | 16.0 | 0.16 | 14.3 | 0.07 | 12.2 | 0.10 | 1.12x | 0.86x |
| unitto | 12.0 | 0.36 | 8.5 | 0.08 | 9.6 | 0.19 | 1.41x | 1.13x |
| **all** | 14.9 | 0.39 | 13.2 | 0.38 | 16.7 | 0.47 | 1.13x | 1.27x |

### Perception tokens by app

| app | hybrid mean | cv | bare mean | cv | acli mean | cv | hybrid/bare | acli/bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| amaze | 61,580 | 0.27 | 59,449 | 0.15 | 57,910 | 0.45 | 1.04x | 0.97x |
| joplin | 49,972 | 0.13 | 26,880 | 0.93 | 55,837 | 0.37 | 1.86x | 2.08x |
| lesspass | 20,108 | 0.07 | 19,264 | 0.02 | 47,051 | 0.53 | 1.04x | 2.44x |
| markor | 49,470 | 0.12 | 30,408 | 0.03 | 88,986 | 0.76 | 1.63x | 2.93x |
| seal | 42,792 | 0.12 | 60,244 | 0.00 | 35,262 | 0.26 | 0.71x | 0.59x |
| unitto | 41,670 | 0.11 | 36,196 | 0.12 | 31,978 | 0.25 | 1.15x | 0.88x |
| **all** | 44,265 | 0.33 | 38,740 | 0.47 | 52,838 | 0.59 | 1.14x | 1.36x |

### Billed input tokens (what ACU tracks)

| | hybrid | bare | acli |
|---|---:|---:|---:|
| billed input, median | 14.44 Mtok | 12.36 Mtok | 13.02 Mtok |
| billed input, mean | 14.14 Mtok | 11.95 Mtok | 15.07 Mtok |
| peak resident context | 113,794 | 107,299 | 115,139 |
| turns | 182 | 160 | 193 |
| perception tokens | 44,265 | 38,740 | 52,838 |

Billed input is the integral of context size over turns, so a token added at turn *i* is charged again at every turn after it. Against bare on the median run: hybrid **1.17x**, acli **1.05x** — a perception ratio does not carry into cost, because a whole run's perception spend is a fraction of a percent of what it bills.

### Where the ACU goes

| per run | hybrid | bare | acli |
|---|---:|---:|---:|
| commands before the first action | 5.33 | 20.00 | 12.75 |
| of those, writing its own tooling | 0.08 | 0.58 | 0.17 |
| looks/task | 3.90 | 0.95 | 3.09 |
| perception tokens per look | 499 | 2,239 | 1,350 |
| actions per look | 2.21 | 3.66 | 1.13 |
| blind multi-action commands | 16.67 | 17.42 | 4.92 |
| turns/task | 6.60 | 5.75 | 6.88 |
| ACU/turn | 0.0812 | 0.0817 | 0.0845 |
| ACU/task | 0.54 | 0.47 | 0.59 |

Across the 24 hybrid/bare cells, one extra look per task costs **0.059 ACU per task** (1.63 ACU over a 28-task run) — the strongest per-cell predictor of ACU after turn count itself. hybrid takes 3.90 looks per task against bare's 0.95, which alone prices at +4.81 ACU per run against an observed gap of +1.92. The cheaper look is spent on more looking: bootstrapping the improvised tooling is 0.6 commands of a 160-turn run, so there is no setup tax to amortise.

### Which observation verb the hybrid arm typed

| verb | calls | share |
|---|---:|---:|
| `hd see --find` | 599 | 50% |
| `hd see (delta on a re-observation)` | 422 | 36% |
| `hd see --full` | 105 | 9% |
| `hd see -q (capture, print nothing)` | 61 | 5% |

Of the 422 plain `hd see` re-observations, 154 (36%) directly followed a `--find` or `-q` and 15 a `--full`. `--find` and `-q` render the whole tree but print only the matches (or nothing), so this revision keys the diff baseline off the rendering the caller was SHOWN: those re-observations diff against the last tree that actually reached the agent rather than answering `# no change since the last see` about a screen it has never seen. `evals/test_seen_baseline.py` is the regression; re-read this share every run, since it decides how much that behaviour is worth.

### What a plain `hd see` printed

| outcome | count | share |
|---|---:|---:|
| whole tree (`screen changed too much to diff`) | 1,024 | 76% |
| delta | 326 | 24% |

Counted over every delta-capable look — the 422 plain `hd see` commands above plus the look each action folds in, which is why the total exceeds the command count. The delta is the reason a re-observation is cheap, and it was discarded 76% of the time. Worst cells: seal|hybrid|1 (183 whole / 18 delta), seal|hybrid|2 (176 whole / 24 delta), markor|hybrid|2 (133 whole / 29 delta).

Mechanism: every rendered line ends in the node's centre `(x,y)`, and the diff matched lines whole, so a list scrolled by one row scored all 40 rows as removed AND re-added — a delta twice the size of the tree, which `see` then correctly discarded for the tree. It is the scrolling apps that pay: Amaze and Seal, whose suites page through file and download lists, printed the whole tree on 91-183 re-observations each, while Joplin's form-driven suite printed 2-29. `evals/bench_scroll_diff.py` is the bench for the fix (match on the line without its index or coordinates, report a row that only moved as one `~ [was]->[now] (x,y)` line): 22% fewer characters per re-observation over the six apps' scroll cases, and whole-tree fallbacks 6/24 -> 1/24, with the screen-turnover and stale-baseline fallbacks intact.

### Replacing a value that is already in a field

| | hybrid | bare | acli |
|---|---:|---:|---:|
| hand-rolled deletion loops | 3 | 5 | 4 |
| runs doing it | 3/12 | 3/12 | 2/12 |

Every arm meets the same fields, and none of the three tools had a verb for emptying one, so the agents sent `KEYCODE_MOVE_END` and a guessed number of backspaces. The count is not knowable from outside the tree — the guesses escalate within a run (`seal|hybrid|1`: 20, 30, 10, 30, 30, 40, 20, 40, 20) and a low one leaves the tail of the old value fused to the new text. `hd type "x" -r` takes the count from the focused node's own text; `evals/test_replace.py` prices it against the guess.

### Did the acli arm use accessibility-cli?

12/12 acli runs invoked the binary. 93 of 738 invocations went through a shell wrapper the agent defined (`A --llm-query`), not the literal name.

| invocation | calls | share |
|---|---:|---:|
| `accessibility-cli action (tap/type/key/adb-*)` | 542 | 73% |
| `accessibility-cli other` | 143 | 19% |
| `accessibility-cli --llm (whole tree)` | 52 | 7% |
| `accessibility-cli screenshot / annotate` | 1 | 0% |

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

