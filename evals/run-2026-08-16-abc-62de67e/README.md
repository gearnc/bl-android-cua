# A/B/C, 16 August 2026 (third matrix of the day) — 36 runs at `62de67e`

6 apps × 3 arms (**hybrid / bare / raw**) × 2 replicates, Normal capability, ~30
machine-verifiable tasks each, one app per child session. **No `acli` arm was run and no archived
`acli` number is quoted here.** Hybrid/bare is comparable with `evals/baseline-2026-08/`; `raw`
has history only in the two earlier matrices of this day, so its ratios are quoted inside this run.

## What was measured

- plugin: `main` @ `62de67e` (the merge of #23, the look-packaging PR), containing **both**
  `skills/android-hybrid-navigation` and `skills/android-raw-navigation` — verified by grepping a
  throwaway child's plugin cache for the raw skill's `SKILL.md` and printing its `ui.py` wrapper,
  not assumed from the snapshot date
- emulator: Android 14 / API 34, 720x1280 @320dpi, F-Droid APKs preinstalled
- apps: markor, amaze (Views), seal, unitto (Compose), joplin, lesspass (React Native)
- arms differ by exactly one paragraph (`suites.ARM_HYBRID` / `ARM_BARE` / `ARM_RAW`): `bare` is
  denied both skills and `hd`, `raw` is denied only `android-hybrid-navigation`/`hd` and told to
  read `android-raw-navigation`'s SKILL.md itself. Neither the wrapper nor any command was pasted
  into a prompt.
- the plugin was not modified between launching the matrix and collecting it. The `hint_batch`,
  `test_dumps.py` and `is_look` changes in the same PR as this archive were written **after**
  collection and are NOT in the measured revision.

## Headline

Ratios against bare — ACU: hybrid **0.85x**, raw **0.63x**. Perception tokens: hybrid **0.44x**,
raw **0.18x**. Billed input (median run): hybrid **0.95x**, raw **0.75x**. Screenshots: hybrid
**0.14x**, raw **0.04x**. Tasks done: hybrid **1.03x**, raw **1.02x** (28.2 / 27.5 / 28.2 of ~30).

**Hybrid beat bare and lost to raw**: raw is **0.74x** hybrid's ACU and **0.41x** its perception
tokens while finishing the same number of tasks, on every stack (compose 0.75x, rn 0.81x, views
0.71x of hybrid's ACU). Tail: ACU CV 0.38 hybrid / 0.32 bare / 0.26 raw, p90 16.6 / 24.9 / 13.6 —
the raw arm's variance-reduction thesis holds against bare, and hybrid's tail is the worst of the
three (max 31.3 ACU on `amaze|hybrid|2`).

## Validity

- **bare arm's perception mode**: this matrix is the harsh framing, not the flattering one —
  11/12 bare runs did visual CUA (≥20 screenshots, median 89), 1/12 improvised tree tooling. So
  hybrid/bare here is *skill vs. visual computer use*, and only 2/12 bare runs wrote or ran a
  dump wrapper of their own (first at command 3–5). Bare rederivation, the quantity `raw` vs.
  `bare` prices, essentially did not happen this time.
- **raw arm adoption**: 12/12 used the method (849 wrapper/`uiautomator dump` invocations, first
  at command 2–10). **Contamination: 0/12 invoked `hd`.** No cell was dropped.
- **bypass**: runs writing device state directly — 4/12 hybrid, 4/12 bare, 5/12 raw; no arm did
  materially less work.
- **dump preflight**: `python3 evals/test_dumps.py markor amaze seal unitto joplin lesspass`
  returned rc=0 with no `problems` for all six apps of the matrix, each launched first. The
  whole-suite invocation still fails on apps outside this matrix (dumps that read files a
  never-launched app has not created, and two suites whose dump contains a single quote); the PR
  that adds this archive lets the script take the suite names so the condition the playbook
  states can be checked on exactly the apps a matrix launches.
- every cell returned structured output; 36/36 collected, no relaunches.

## Mechanism (what the PR acts on)

The previous PR (#23) closed the *packaging* gap: a look now costs hybrid **429** perception
tokens against the raw wrapper's **329** on the same screens. What is left is entirely the
**number** of looks — hybrid takes **4.24 looks per task** against raw's **2.71**, because it
chains **1.19 actions per look** against raw's **2.11**. Raw's SKILL.md teaches chaining as the
method; hd has `-n` and `hd run`, SKILL.md leads with both, and `hint_no_see` names `-n` once a
session — and hybrid still ran one action per look. At 0.035 ACU per look per task, hybrid's
excess looking prices at ~+1.5 ACU a run, which is half the hybrid/raw ACU gap.

Counting a look: an hd action verb without `-n` prints a tree, so it *is* a look. The report's
`is_look` counted only `see`/`find` before this PR, which credited hybrid with a third of the
looks it took and inflated its tokens-per-look to 883 — the correction is what shows the two arms
pay the same price per look.

Unfixed and priced here for the next PR: 82 of the hybrid arm's 333 look-only commands (10/12
runs) were still a look followed by nothing but `hd tap <index>`, even though `hd tap "PAT"` was
typed on 200 of 657 taps (30%, up from 0% at `477c380`).

## Files

`runs.json` (cell → session id), `metrics.json` (perception, ACU, billed input, turns, peak
context), `tasks.json`, `bypass.json`, `exec_commands.json` (what the adoption sections read),
`report.md` (generated by `evals/make_report.py`).
