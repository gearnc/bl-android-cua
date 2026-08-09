# Baseline, August 2026 — 126 runs

21 apps × hybrid/bare × 3 reps, Normal capability, ~30 tasks each, on the plugin as of PR #1
(so: Compose detection, swipe scaling, `hd type` quoting and the `hd` launcher fixed, but
**before** `hd see --diff` landed in PR #2).

Headline: at equal reliability (~28/30 either arm) the skill was at parity on cost — ACU 1.07x,
perception tokens 0.94x — while spending 1.35x the iterations and 1.43x the exec calls. Its
advantage was the tail (worst hybrid run 59.5k perception tokens vs 186k for bare) and half the
screenshots. `report.md` is the full writeup.

Any future run should be compared against these files rather than against the README's original
claims, which were measured differently.

- `runs.json` — cell → session id (the sessions themselves are the ultimate audit trail)
- `metrics.json` — ACU, perception tokens, screenshots, iterations, exec calls per cell
- `tasks.json` — n_done / n_partial / n_failed per cell
- `bypass.json` — UI-bypassing shortcut commands per cell
