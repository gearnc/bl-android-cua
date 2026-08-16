# A/B/C, 16 August 2026 (third matrix of the day) — 36 runs at `23ab01b`

6 apps × 3 arms (**hybrid / bare / raw**) × 2 replicates, Normal capability, ~30
machine-verifiable tasks each, one app per child session. **No `acli` arm was run and no archived
`acli` number is quoted here.** Hybrid/bare is comparable with `evals/baseline-2026-08/`; `raw`
has history in the two earlier matrices of the same day (`run-2026-08-16-abc`, `-477c380`), but
its ratios are quoted inside this run.

## What was measured

- plugin: `main` @ `23ab01b`, containing **both** `skills/android-hybrid-navigation` and
  `skills/android-raw-navigation` — verified by grepping a throwaway child's plugin cache for the
  revision's symbols and for the raw skill's `SKILL.md`, not assumed from the snapshot date
- emulator: Android 14 / API 34, 720x1280 @320dpi, F-Droid APKs preinstalled
- apps: markor, amaze (Views), seal, unitto (Compose), joplin, lesspass (React Native)
- arms differ by exactly one paragraph (`suites.ARM_HYBRID` / `ARM_BARE` / `ARM_RAW`): `bare` is
  denied both skills and `hd`, `raw` is denied only `android-hybrid-navigation`/`hd` and told to
  read `android-raw-navigation`'s SKILL.md itself. Neither the wrapper nor any command was pasted
  into a prompt.
- two harness fixes landed **before** launch, not during: the lesspass verification dump contained
  single quotes (so the child's `adb shell '{dump}'` spliced it apart) and never read the RN
  AsyncStorage DB, and `test_dumps.py` now mirrors that same quoting. The plugin itself was not
  modified between launching the matrix and collecting it — the `hd.py` change in the PR that adds
  this archive was written **after** collection and is NOT in the measured revision.

## Headline

Ratios against bare — ACU: hybrid **0.88x**, raw **0.64x**. Perception tokens: hybrid **0.30x**,
raw **0.12x**. Billed input (median run): hybrid **1.14x**, raw **0.93x**. Iterations: hybrid
**1.10x**, raw **0.86x**. Tasks done: hybrid **0.99x**, raw **0.97x** (27.8 / 28.2 / 27.5 of ~30).

**Hybrid beat bare but lost to raw**: 16.5 ACU against raw's 11.9 (**1.39x**) at the same
reliability. The bare arm was expensive here because it ran mostly visual (median 100
screenshots), so hybrid's 0.30x perception ratio is priced against screenshots, not against tree
tooling. ACU CV is flat across arms (0.36 / 0.37 / 0.36); the tail is where bare loses — perception
p90 228,743 and max 650,887, against hybrid 63,965 / 91,663 and raw 24,431 / 30,846.

Perception tokens are not billed cost: integrating resident context over turns, hybrid is the
*most* expensive arm (median 12.94 Mtok vs. bare 11.33, raw 10.51). A cheaper look that is taken
more often, in more turns, is not a cheaper run.

## Validity

- **bare arm's perception mode**: **visual CUA**, unlike the previous two matrices — 0/12 runs at
  ≤5 screenshots, 10/12 at ≥20, median 100 screenshots. Only 3/12 wrote or ran their own dump
  wrapper (first at command 3–24). So this run measures *skill vs. visual computer use*, and the
  `raw` vs. `bare` gap prices a rederivation that 9/12 bare cells never performed.
- **raw arm adoption**: 12/12 used the method (908 wrapper/`uiautomator dump` invocations, first
  at command 2–11). **Contamination: 0/12 invoked `hd`.** No cell was dropped.
- **bypass**: runs writing device state directly — 7/12 hybrid, 5/12 bare, 7/12 raw; no arm did
  materially less work, but the counts are not identical and per-app ACU should be read with that.
- **dump preflight**: `test_dumps.py` reported no `problems` for any app, but several apps' dump
  commands exited non-zero (they read files a freshly installed app has not created) and the
  script does not fail on that, so the playbook's "rc=0 for every app" was not strictly met. The
  six matrix apps were launched and dumped by hand and their final state dumps graded cleanly, so
  the matrix stands.
- collection cross-check: two bare cells' iteration counts differ from their `iteration_stats`
  event counts by 4 (`seal|bare|1` 146 vs. 150, `joplin|bare|1` 159 vs. 163). No data was lost.

## Mechanism (what the PR acts on)

Hybrid's look costs **603 perception tokens against raw's 282** on the same screens — 2.1x for a
strictly better rendering. Two components of that gap carry no information at all:

- **constant indentation.** `render()` indented each line by `min(depth, 6)`; on all six eval apps
  every informative node clamped at the ceiling, so a tree arrived with a 12-space prefix on 100%
  of its lines — **22% of the printed bytes of a look**. Re-basing on the shallowest shown node
  keeps relative nesting and removes the constant.
- **the views TIP.** It was printed from the render path on every plain `hd see` of a large
  labeled tree; hybrid typed **202 such looks** in this run, buying one sentence ~200 times.

Measured over the six apps by `evals/bench_look_overhead.py`: 10,432 → 8,104 printed bytes
(**-22%**), hybrid/raw bytes per look 1.75x → 1.36x, TIP 2 → 1 over two looks at the same screen,
relative nesting preserved.

Unfixed and priced here for the next PR: hybrid still typed 383 plain `hd see` re-observations,
many of them to turn a label it already knew into an index for the following `hd tap <index>` —
the same label-resolution tax the previous matrix found, still not being paid down by the hint.

## Files

`runs.json` (cell → session id), `metrics.json` (perception, ACU, billed input, turns, peak
context), `series.json` (the context-vs-turn samples the billed integral uses), `tasks.json`,
`bypass.json`, `exec_commands.json` (what the adoption sections read), `report.md` (generated by
`evals/make_report.py`).
