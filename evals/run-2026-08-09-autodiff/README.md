# Run, 2026-08-09 (late) — 24 cells, plugin `main` @ 0012eae

The same matrix as [the earlier run that day](../run-2026-08-09/) — 6 apps (markor/amaze Views,
seal/unitto Compose, joplin/lesspass RN) × hybrid/bare × 2 replicates, Normal capability, ~30
machine-verifiable tasks each — re-run against `main` @ `0012eae`, i.e. **with** PR #4: the delta
is now the default for a re-`see`, and `hd see -q` / `hd find` exist. The children's plugin cache
was verified byte-identical to that revision before launch.

Headline: reliability parity (28.0/30 hybrid vs 27.8/30 bare), ACU parity
(**0.95x**, 11.9 vs 12.6), perception tokens **0.51x** (33.6k vs 66.3k), screenshots **0.13x**
(4 vs 33). Billed input — what ACU actually tracks — is at parity again: **1.04x** on the median
run (12.69 vs 12.19 Mtok). The tail is where the arms separate: worst hybrid run 50.8k perception
tokens against bare's 173.9k, and hybrid's p90 39.4k against bare's 82.8k. Note the direction of
that tail has flipped since the previous run, where hybrid owned the two most expensive runs.

**Bare-arm caveat — this run is the opposite of the last one.** 6/12 bare runs did real visual
CUA (≥20 screenshots, up to 111), only 2/12 improvised tree tooling (≤5), 4 in between; the
median bare run took 22 screenshots. So this run measures *skill vs. mostly-visual computer use*
— the flattering framing — where the 2026-08-09 run and the August baseline measured *skill vs.
agent-improvised tree tooling*. The 0.51x perception ratio is not comparable to the earlier
0.50x for that reason: same number, different bare arm. `report.md` now derives this sentence
from the screenshot distribution instead of asserting it.

## Mechanism: the delta default was opted out of, 717 times

PR #4 made the delta the default because the previous run showed `--diff` was a flag nobody
typed (8 uses across 12 runs). This run shows the fix did not land either — for a different
reason. Hybrid observation verbs, all 12 runs:

| verb | calls | share |
|---|---:|---:|
| `hd see --no-diff` (opt out of the delta) | 717 | 55% |
| `hd see --find` | 410 | 32% |
| `hd see` (the delta default) | 130 | 10% |
| `hd see --full` | 36 | 3% |
| `hd see -q` (capture, print nothing) | 4 | 0% |

The delta path actually printed **15 times across all 12 hybrid runs**, and 33 more observations
fell back to the whole tree because the screen had turned over. Every run typed `--no-diff`
before it had ever seen a delta — median 11th shell command of the run, as early as the 6th
(`joplin|hybrid|2`) — so this is not agents rejecting the delta after seeing one. They
learned the escape hatch from the documentation: `--no-diff` had its own line in the `hd` verb
list, its own sentence in SKILL.md's core loop, and was named in the header of every delta
(“`hd see --no-diff` for the whole tree”). An opt-out advertised three times over is an opt-out
that gets typed.

That habit is expensive: measured over 8 real observe→act→observe steps in Amaze and Unitto, a
`--no-diff` re-read costs 16,529 chars against the default's 3,507 — the default is **79%
cheaper**, ~407 tokens
per re-observation, up to 24.3k tokens per run at this run's call volume against a measured mean
of 33.6k. `evals/test_no_diff_affordance.py` regresses the affordance (the flag keeps working,
nothing advertises it) and re-measures the gap.

Second finding, in the harness rather than the plugin: `gather.exec_commands` required the
`(shell: <id>)` suffix that the events API only emits for single-line commands, so every
heredoc and `python3 -c` block was silently dropped from `bypass.json` (48 of 56 commands
captured in the first cell checked) — exactly the shape a state-writing `adb shell` hides in.
Collection re-ran against the fixed parser and every cell's command count now matches the event
list's own total, which is how the gap was caught. Fixed in the same PR; the
counts here are from the fixed parser (writes 7 hybrid vs 6 bare, intents 1 vs 0 — balanced, so
the ACU comparison stands).

## Files

- `runs.json` — cell → session id (the sessions themselves are the ultimate audit trail)
- `metrics.json` — ACU, perception tokens, screenshots, iterations, exec calls per cell
- `tasks.json` — n_done / n_partial / n_failed per cell
- `bypass.json` — UI-bypassing shortcut commands per cell
- `billed.json` — turns, peak context and billed input tokens per cell
- `report.md` — the full writeup

Billed input is the trapezoid integral of `current_context_tokens` over `iteration_count`,
sub-sampled at 10 points per run including the first and last event (`billed.py`). A whole run's
perception spend is ~0.26% of what it bills, so a perception ratio is not a cost ratio — as in
the previous run, the skill's measured value here is reliability parity at cost parity, plus a
much shorter tail.
