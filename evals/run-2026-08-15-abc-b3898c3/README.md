# A/B/C, 15 August 2026 (second matrix of the day) — 36 runs

6 apps × 3 arms (hybrid / bare / acli) × 2 replicates, Normal capability, ~30 machine-verifiable
tasks each, one app per child session. This is the first matrix run **after** `hd tap "PAT"`
(#17), so it is the one that prices that verb's adoption; `evals/run-2026-08-15-abc/` is the same
matrix at `5ec78b6`, the revision before it. Hybrid/bare is comparable with `baseline-2026-08/`,
`run-2026-08-14-abc/` and `run-2026-08-15-abc/`; **acli has no history before 14 August** — do not
read an acli number against the archived two-arm baselines.

## What was measured

- plugin: `main` @ `b3898c3` — includes `hd tap "PAT"` from #17, verified by grepping the child
  snapshot's plugin cache for `tap_pattern` rather than assumed
- accessibility-cli: `0.1.0` @ `03cfeb3db1ecd37375f370edfe86b8ffbfa9037f`, on PATH in the child
  snapshot, `--version` checked in a throwaway child before launch
- emulator: Android 14 / API 34, 720x1280 @320dpi, F-Droid APKs preinstalled
- apps: markor, amaze (Views), seal, unitto (Compose), joplin, lesspass (React Native)
- pre-launch: `test_acli.py` `problems=none` for all six apps; `test_dumps.py` reported no `BAD`
  markers for any matrix app, but exited `rc=1` on four of them — every one of those failures is
  a `cat`/`ls` of app state a fresh install has not written yet, not a dump error. The playbook
  asks for `rc=0`; this run was launched on `problems=none` plus that manual check instead, and
  the caveat is recorded here rather than smoothed over.

## Headline

Ratios against bare — ACU: hybrid **1.11x**, acli **1.18x**. Perception tokens: hybrid **0.79x**,
acli **0.84x**. Iterations: hybrid **1.16x**, acli **1.23x**. Tasks done: hybrid **1.00x**, acli
**0.99x** (28.1 / 28.1 / 27.9 of ~30). Screenshots (mean): hybrid 5, bare 23, acli 15.

Billed input — the integral of resident context over turns, which is what ACU tracks — moves
further the same way: median run hybrid **1.20x** bare, acli **1.39x**. A cheaper look is not a
cheaper run. Hybrid takes 3.32 looks per task against bare's 2.20 at 587 perception tokens per
look; across the 24 hybrid/bare cells one extra look per task prices at 0.062 ACU per task, which
alone accounts for +1.96 ACU against the observed +1.53 gap. Tails: worst perception run is
bare's (238,832 on `seal|bare|2`, a 145-screenshot visual run) against hybrid's 75,933.
`report.md` is the full writeup.

## Validity

- all 36 cells settled in `waiting_for_user` with structured output; none graded from prose
- **bare-arm mode**: mostly visual. At ≤5 screenshots = improvised tree tooling and ≥20 = visual
  CUA: 1/12 improvised tooling, 3/12 visual CUA, 8/12 in between; median 10 screenshots over ~30
  tasks. So this is nearer *skill vs. visual computer use* — the flattering framing — than *skill
  vs. agent-improvised tree tooling*. Re-check the split every run; it has flipped between runs
  of the same matrix.
- **acli adoption**: 12/12 acli cells invoked the binary; no cell dropped. 301 of the 837
  invocations went through a wrapper the agent wrote, so literal-name counts are a floor.
- **bypass**: runs writing device state directly are 7/12 hybrid, 5/12 bare, 5/12 acli — no arm
  skipped a materially different amount of UI work.
- dump-return-code caveat above.

## What the run bought

The mechanism this run funded is in `report.md` under "Looks bought to turn a label into an
index": 100 of hybrid's 252 look-only commands, in 11/12 runs, were a look followed by nothing
but `hd tap <index>`, while `hd tap "PAT"` — shipped in #17 and led with in SKILL.md — took only
126 of 781 taps (16%). Documentation moved that idiom from 115/236 to 100/252 and stopped, so the
fix in this PR is hd naming the verb itself at the moment the caller pays for its absence
(`evals/test_tap_hint.py`).
