# Run, 2026-08-09 — 24 cells, plugin `main` @ 367fe0a

6 apps (2 per toolkit: markor/amaze Views, seal/unitto Compose, joplin/lesspass RN) × hybrid/bare
× 2 replicates, Normal capability, ~30 machine-verifiable tasks each. Measured the plugin as of
`367fe0a` — i.e. **with** `hd see --diff` (PR #2) and the eval harness (PR #3), and before the
auto-diff change this run motivated.

Headline vs. the [August baseline](../baseline-2026-08/) (126 runs, pre-`--diff`): reliability is
still at parity (28.2/30 hybrid vs 28.4/30 bare), ACU is still at parity (1.02x, was 1.07x), and
perception tokens moved from 0.94x to **0.50x** hybrid/bare. The tail is where the arms separate:
worst hybrid run 79k perception tokens vs 186k bare; bare p90 32.6k vs hybrid 20.6k.

**Bare-arm caveat.** 5/12 bare runs improvised tree tooling (<=5 screenshots), 2/12 did real
visual CUA (94 and 121 screenshots), 5 sat in between. The bare arm's perception mean is
dominated by those two runs, so the headline ratio is "skill vs. a mix of improvised tree
tooling and pixels", not "skill vs. screenshots". `report.md` states this per run.

**Mechanism found.** `hd see --diff` was effectively unadopted: 8 invocations across all 12
hybrid runs, zero in 8 of them, against 217 plain/`--full` re-reads. The two most expensive
hybrid runs are both re-read loops — `amaze|hybrid|1` paged the full tree with
`hd see --full | head -40` / `sed -n '55,100p'` 14 times (246 iterations, 49.3k tokens), and
`seal|hybrid|1` fell back to 33 screenshots to read Compose toggle state (79.2k tokens). The
saving existed but was behind a flag nobody typed, which is why the fix makes the diff the
default for a re-`see`.

- `runs.json` — cell → session id (the sessions themselves are the ultimate audit trail)
- `metrics.json` — ACU, perception tokens, screenshots, iterations, exec calls per cell
- `tasks.json` — n_done / n_partial / n_failed per cell
- `bypass.json` — UI-bypassing shortcut commands per cell
- `report.md` — the full writeup
