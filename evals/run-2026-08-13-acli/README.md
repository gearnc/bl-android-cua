# Run, 2026-08-13 — 36 cells, three arms, plugin `main` @ 342b474

Third A/B/**C**, same shape as [`run-2026-08-12-acli`](../run-2026-08-12-acli/): 6 apps × 2
replicates (markor/amaze Views, seal/unitto Compose, joplin/lesspass RN, ~30 machine-verifiable
tasks each, Normal capability, fixed `adb` verification dump) × 3 arms differing by exactly one
prompt paragraph —

| arm | prompt paragraph | what it had |
|---|---|---|
| `hybrid` | `ARM_HYBRID` | whatever tooling it has, i.e. the skill |
| `bare` | `ARM_BARE` | the skill denied, nothing offered instead |
| `acli` | `ARM_ACLI` | the skill denied, pointed at `accessibility-cli` |

Measured revisions, verified on a child VM before launch, not assumed:

* plugin `main` @ `342b474` — i.e. everything through PR #14: the seen-rendering baseline (#10),
  `--find`/`find` printing the tree on a miss (#11, #13), actions folding their own look with
  `-n` to opt out (#12), the ambiguous-re-match tap guard and `hd type -r` (#14);
* `accessibility-cli` `0.1.0` @ `03cfeb3` (DioxusLabs/accessibility-cli), `cargo install`ed into
  the snapshot and on `PATH`;
* emulator Android 14 / API 34 at 720×1280 @320dpi, all six verification dumps `rc=0` and
  `test_acli.py` `problems=none` before any child was launched (`hd see` 427–2,684 chars against
  `accessibility-cli --llm` 29–749 on the same six screens).

All 36 cells returned structured output and an uncensored final `context_growth_update`. Ratios
are against `bare`. Full writeup in [`report.md`](report.md).

## Headline

ACU **1.13x** hybrid / **1.27x** acli. Perception tokens **1.14x** / **1.36x**. Screenshots
**0.35x** / **1.01x**. Tasks done 27.6 / 28.0 / 28.0 of ~30. Billed input (resident context
integrated over turns) **1.17x** / **1.05x** on the median run.

**The parity of 2026-08-12 did not hold**: hybrid is back to 1.13x bare ACU on a bare arm that
was mostly doing visual CUA. The tail is where the skill still shows: worst run 26.7 ACU against
acli's 33.3, 7.0 screenshots a run against 19.8 and 20.0, and perception cv 0.33 against 0.47 and
0.59. What moved against it is looks: 3.90 looks/task against bare's 0.95, at 499 perception
tokens a look against bare's 2,239 — the cheap look is being spent, not saved, and one extra look
per task prices at 0.059 ACU/task across the 24 hybrid/bare cells.

## The defect this run found

**76% of the hybrid arm's delta-capable looks printed the whole tree anyway** — 1,024
`screen changed too much to diff` against 326 deltas, counted per session from its events
(`diff_outcomes.json`). Every rendered line ends in the node's centre `(x,y)` and the diff matched
lines whole, so a list scrolled by one row scored all 40 rows as removed AND re-added: a delta
twice the size of the tree, which `see` then correctly discarded for the tree. The scrolling
suites pay it (Amaze and Seal 91–183 whole trees per run; form-driven Joplin 2–29), which is the
same set of apps carrying hybrid's ACU gap.

Fixed in the same PR by matching on the line without its index or coordinates and reporting a row
that only moved as one `~ [was]->[now] (x,y)` line. `evals/bench_scroll_diff.py` prices both
revisions on the same screens: 22% fewer characters per re-observation, whole-tree fallbacks
6/24 → 1/24, screen-turnover and stale-baseline fallbacks intact, and it asserts every
renumbering names the same node under both indexes.

## Bare-arm caveat — read before quoting any ratio

Counting a bare run as *improvised tree tooling* at ≤5 screenshots and *visual CUA* at ≥20:
**2/12 improvised, 3/12 visual, 7 in between; median 14 screenshots.** So this leans towards
"skill vs. visual computer use" — the flattering framing, as in the two previous acli runs and
unlike [`baseline-2026-08`](../baseline-2026-08/), where the bare arm rebuilt tree tooling almost
every time. Perception ratios are not comparable across runs whose bare arms did different
things; hybrid/bare ACU is.

**Do not compare the acli column against `baseline-2026-08` or `run-2026-08-09*`** — those runs
had two arms and never ran it.

## acli adoption: 12/12

Every acli cell invoked the binary (738 invocations, 93 of them through a wrapper the agent
defined rather than the literal name), so no cell is dropped from the ratio. Only 52 of those
calls are `--llm` whole-tree looks; 542 are its adb action wrapper. Where it cost: **LessPass
2.43x bare ACU and Markor 1.52x**, with perception 2.93x on Markor and 2.44x on LessPass — the
selector-then-fallback loop `test_acli_gaps.py` prices, ending in the 20.0 screenshots a run this
arm still takes.

## Bypass counts

6/12 hybrid, 5/12 bare, 7/12 acli runs wrote device state directly (`adb shell mkdir`,
`settings put`, deep-link intents) instead of driving the UI. Close enough across arms that no
app's ACU comparison is void on that ground.

## Files

| file | what |
|---|---|
| `runs.json` | cell (`app\|arm\|rep`) → child session id |
| `metrics.json` | per cell: ACU, turns, perception tokens, screenshots, capture checks |
| `tasks.json` | per cell: structured-output task counts |
| `bypass.json` | per cell: commands that wrote device state instead of driving the UI |
| `exec_commands.json` | per cell: every `shell_process_started` command (the adoption sections read this) |
| `billed.json` | per cell: billed input tokens, peak resident context, turns |
| `diff_outcomes.json` | per hybrid cell: whole-tree vs delta outcomes of `hd see`, from event search |
| `report.md` | the generated report |
