# Run, 2026-08-12 — 36 cells, three arms, plugin `main` @ 7d75266

Second A/B/**C**, same shape as [`run-2026-08-10-acli`](../run-2026-08-10-acli/): 6 apps × 2
replicates (markor/amaze Views, seal/unitto Compose, joplin/lesspass RN, ~30 machine-verifiable
tasks each, Normal capability, fixed `adb` verification dump) × 3 arms differing by exactly one
prompt paragraph —

| arm | prompt paragraph | what it had |
|---|---|---|
| `hybrid` | `ARM_HYBRID` | whatever tooling it has, i.e. the skill |
| `bare` | `ARM_BARE` | the skill denied, nothing offered instead |
| `acli` | `ARM_ACLI` | the skill denied, pointed at `accessibility-cli` |

Measured revisions, verified on a child VM before launch, not assumed:

* plugin `main` @ `7d75266` — i.e. everything through PR #13: baselines keyed off the rendering
  the caller was shown (#10), `--find`/`find` printing the tree on a miss (#11, #13), and actions
  folding their own look with `-n` to opt out (#12);
* `accessibility-cli` `0.1.0` @ `03cfeb3` (DioxusLabs/accessibility-cli), `cargo install`ed into
  the snapshot and on `PATH`;
* emulator Android 14 / API 34 at 720×1280 @320dpi, all six verification dumps `rc=0` and
  `test_acli.py` `problems=none` before any child was launched (`hd see` 427–2,684 chars against
  `accessibility-cli --llm` 29–749 on the same six screens).

All 36 cells returned structured output and an uncensored final `context_growth_update`
(`censored=false` on every row of `metrics.json`; page size 40, one `details` call per event).
Ratios are against `bare`. Full writeup in [`report.md`](report.md).

## Headline

ACU **0.97x** hybrid / **1.14x** acli. Perception tokens **0.76x** / **0.89x**. Screenshots
**0.28x** / **0.92x**. Tasks done 28.3 / 27.7 / 27.9 of ~30. Billed input (resident context
integrated over turns) **1.15x** / **1.10x** on the median run.

**The skill reached ACU parity for the first time** — 1.13x on 2026-08-10, 1.10x on 2026-08-11,
0.97x here — while keeping the perception and screenshot ratios it already had. The three
changes between those runs were all about not paying twice for one look, and the mechanism they
were aimed at moved: actions per look 1.73 → 2.16 and hybrid's looks/task 4.14 → 3.34 against
bare's 2.63. Hybrid is also the arm that least often looks twice in a row — 21 of its 174
pure-observation commands follow another observation, against 168/314 bare and 399/658 acli.

It is parity, not a win: the arms are within noise of each other on ACU (cv 0.35/0.38), and
hybrid still bills 1.15x the median input tokens because it holds more looks in context. What
the skill buys at parity is the tail and the failure mode — worst run 18.7 ACU against bare's
20.0 and acli's 25.4, worst perception 59k against 93k and 74k, 4.8 screenshots a run against
17.0, and no run that fell back to pixels.

## Bare-arm caveat — read before quoting any ratio

Counting a bare run as *improvised tree tooling* at ≤5 screenshots and *visual CUA* at ≥20:
**2/12 improvised, 4/12 visual, 6 in between; median 12 screenshots.** So this run leans towards
"skill vs. visual computer use" — the flattering framing, the same one as
[`run-2026-08-10-acli`](../run-2026-08-10-acli/) and unlike
[`baseline-2026-08`](../baseline-2026-08/), where the bare arm rebuilt tree tooling almost every
time. Perception ratios are not comparable across runs whose bare arms did different things;
hybrid/bare ACU is.

**Do not compare the acli column against `baseline-2026-08` or `run-2026-08-09*`** — those runs
had two arms and never ran it.

## acli adoption: 12/12

Every acli cell invoked the binary (844 invocations, 303 of them through a shell alias the agent
defined rather than the literal name), so no cell is dropped from the ratio. But adoption counts
the binary being *typed*, and 55% of those calls are `--adb-tap`/`--adb-back`/`--type`, i.e. its
adb wrapper; only 98 are whole-tree looks.

Where it cost: **React Native**, ACU 1.55x bare and perception 1.67x, with 29.8 screenshots a run
against hybrid's 3.2. The mechanism is the one `test_acli_gaps.py` prices — a selector-only
action API that has to re-find the node by string, on a toolkit whose titles are often a
content-description or absent. On RN the arm typed 185 selector actions and fell back to 36
`--adb-tap`s and 67 `screencap`s; on Compose, where `--llm` prints no elements at all, the
selectors were abandoned outright (5 selector actions against 8 coordinate taps and 36
screencaps).

## Bypass counts

4/12 hybrid, 6/12 bare, 4/12 acli runs wrote device state directly (`adb shell mkdir`,
`settings put`, deep-link intents) instead of driving the UI. Balanced enough that no app's ACU
comparison is void on that ground, and unchanged in shape from the previous run.

## Defects this run paid for, fixed in the same PR

1. **`hd tap N` could tap a sibling.** Before acting, `tap` re-dumps and re-finds the node by
   (class, text, desc, id) to catch a shifted layout. On a form whose fields share one
   resource-id and are all empty — every RN text form — all three fields have the same identity,
   the search returns the first, and the tap lands on the row above the one the caller indexed,
   under a `# node moved; tapping fresh coords` line that reads like the guard working. It fired
   17 times across the 12 hybrid runs. The index is the disambiguator when the identity is not
   unique, so an ambiguous re-match now keeps the caller's coordinates
   (`evals/test_tap_identity.py`: 3/3 taps land on the indexed field, 1/3 before).
2. **No way to replace a value already in a field.** `hd type` appends, so editing an existing
   value fell outside the skill: agents left it and hand-rolled
   `keyevent MOVE_END; for i in $(seq 30); do keyevent 67; done` — 28 such commands over 8 of the
   12 hybrid runs, with the guess escalating on the same field (`seal|hybrid|1`: 20, 30, 10, 30,
   30, 40, 20, 40, 20). hd holds the field's text and never had to guess: `hd type "x" -r` now
   deletes exactly `len(text)` characters in one `input keyevent` call
   (`evals/test_replace.py`). Both other arms hit the same wall (12 and 9 commands) — it is a
   suite-wide cost, not a hybrid one, but only one of the three tools can fix it.

## Files

| file | what |
|---|---|
| `runs.json` | cell (`app\|arm\|rep`) → child session id |
| `metrics.json` | per cell: ACU, turns, perception tokens, screenshots, billed input, capture checks |
| `tasks.json` | per cell: structured-output task counts |
| `bypass.json` | per cell: commands that wrote device state instead of driving the UI |
| `exec_commands.json` | per cell: every `shell_process_started` command (the adoption sections read this) |
| `billed.json` | per cell: billed input tokens, peak resident context, turns |
| `report.md` | the generated report |
