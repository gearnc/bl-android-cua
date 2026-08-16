# A/B/C, 16 August 2026 — 36 runs

6 apps × 3 arms (**hybrid / bare / raw**) × 2 replicates, Normal capability, ~30
machine-verifiable tasks each, one app per child session. **No `acli` arm was run and no archived
`acli` number is quoted here.** Hybrid/bare is comparable with `evals/baseline-2026-08/` and the
earlier runs; `raw` — the `android-raw-navigation` method, i.e. a `uiautomator dump` wrapper,
action chaining, one look per command and nothing else — has no history before this run, so its
ratios are only meaningful inside it.

## What was measured

- plugin: `main` @ `0bfdb63`, containing **both** `skills/android-hybrid-navigation` and
  `skills/android-raw-navigation` — verified by grepping a throwaway child's plugin cache for the
  raw skill's `SKILL.md` and wrapper block, not assumed from the snapshot date
- emulator: Android 14 / API 34, 720x1280 @320dpi, F-Droid APKs preinstalled
- apps: markor, amaze (Views), seal, unitto (Compose), joplin, lesspass (React Native)
- arms differ by exactly one paragraph (`suites.ARM_HYBRID` / `ARM_BARE` / `ARM_RAW`): `bare` is
  denied both skills and `hd`, `raw` is denied only `android-hybrid-navigation`/`hd` and told to
  read `android-raw-navigation`'s SKILL.md itself. Neither the wrapper nor any command was pasted
  into a prompt.
- the plugin was not modified between launching the matrix and collecting it. The `hd` diff
  change in the same PR as this archive was written **after** collection and is NOT in the
  measured revision.

## Headline

Ratios against bare — ACU: hybrid **0.81x**, raw **0.63x**. Perception tokens: hybrid **0.35x**,
raw **0.15x**. Iterations: hybrid **0.94x**, raw **0.81x**. Tasks done: hybrid **0.99x**, raw
**1.00x** (28.0 / 28.2 / 28.2 of ~30). Screenshots (mean): hybrid 4, bare 88, raw 3.

Billed input — resident context integrated over turns, which is what ACU tracks — agrees for once:
median run hybrid **0.95x** bare, raw **0.73x**.

**Hybrid vs. raw is the number this design bought, and it went against `hd`:** raw ran at 0.78x
hybrid's ACU and 0.45x its perception tokens for the same tasks done. The method alone got the
win; `hd`'s machinery (framework adaptation, caching/diffing, selectors, verification) did not pay
for its own overhead in this suite — hybrid took 2.93 looks/task against raw's 2.44 at a
comparable per-look price. `report.md` is the full writeup.

## Validity

- all 36 cells settled in `waiting_for_user` with structured output; none graded from prose
- **bare-arm mode**: mostly **visual CUA**, not improvised tree tooling. At ≤5 screenshots =
  improvised tooling and ≥20 = visual CUA: 1/12 improvised, 11/12 visual, median 100 screenshots
  over ~30 tasks. So this run mostly measures *skill vs. visual computer use* — the flattering
  framing. It has flipped between runs of the same matrix; re-check it every time.
- **raw-arm adoption / contamination**: 12/12 raw cells drove the emulator with the wrapper (781
  invocations, first at command 2–13), 0/12 invoked `hd`. **No cell dropped**, so the raw ratios
  are about the method and not a fallback.
- **bare-arm rederivation**: only 3/12 bare cells wrote or ran a dump wrapper of their own. The
  rederivation `raw` exists to price mostly did not happen, so raw-vs-bare here is the method
  against visual CUA rather than against a bare agent's own version of the method.
- **bypass balance**: runs writing device state directly are 5/12 hybrid, 4/12 bare, 6/12 raw —
  raw's edge is in the direction that would flatter it, which is worth remembering before reading
  its ACU ratio as pure method.
- **dump preflight**: `test_dumps.py` reported `problems=[]` for all six apps, but several apps'
  dump commands exited non-zero (they read app files that do not exist in a freshly installed
  app) and the script does not fail on that. The playbook's strict "rc=0 for every app" condition
  was therefore not met, though every per-app tree dumped and the final state dumps graded
  cleanly. `test_dumps.py` should be made to exit non-zero on a non-zero rc.

## What the run justified changing

68% of the hybrid arm's delta-capable looks (413 of 607) printed `screen changed too much to
diff` and paid for a whole tree. Reproduced on the emulator against this revision: the delta
already collapses a scrolled row to one `~` line, but it re-prints every **removed** node in full,
so closing Amaze's drawer (28 nodes gone, nothing else changed) cost 2,482 characters against a
2,313-character tree. Naming a removal by the index the caller read it under and collapsing a
constant-shift renumbering into one line takes that re-observation to 310 characters.
`evals/bench_delta_shape.py` prices it.

## Files

- `runs.json` — cell → session id (the sessions are the ultimate audit trail)
- `state.json` — final state, ACU and completion detail per cell
- `metrics.json` — ACU, perception/context/billed tokens, iterations, exec calls, screenshots
- `tasks.json` — n_done / n_partial / n_failed per cell
- `bypass.json` — UI-bypassing shortcut commands per cell
- `exec_commands.json` — every captured `shell_process_started` command, per cell; the adoption,
  verb-mix, focus-hunt, raw-adoption and rederivation sections are derived from it
- `diff_outcomes.json` — whole-tree vs. delta outcomes per hybrid cell
- `report.md` — generated by `evals/make_report.py` from the files above
