# Run, 2026-08-11 — 36 cells, three arms, plugin `main` @ f79f502

Same matrix as [`run-2026-08-10-unseen`](../run-2026-08-10-unseen/) — 6 apps × 3 arms × 2
replicates, ~30 machine-verifiable tasks each, Normal capability, fixed `adb` verification dump —
against the revision that shipped the printed-baseline fix (#10).

| arm | prompt paragraph | what it had |
|---|---|---|
| `hybrid` | `ARM_HYBRID` | whatever tooling it has, i.e. the skill |
| `bare` | `ARM_BARE` | the skill denied, nothing offered instead |
| `acli` | `ARM_ACLI` | the skill denied, pointed at `accessibility-cli` |

Measured revisions, verified before launch:

* plugin `main` @ `f79f502`; a throwaway child's plugin cache greps the `#10` symbol
  (`if not quiet and not find:`) and its `hd.py` md5 (`b8bafcc7…`) equals this checkout's, rather
  than the snapshot date being trusted;
* `accessibility-cli` `0.1.0` @ `03cfeb3` (DioxusLabs/accessibility-cli), on `PATH` in the child
  snapshot, `test_acli.py` `problems=none` for all six apps (`--llm` 29–749 chars against
  `hd see`'s 504–2811);
* emulator Android 14 / API 34 at 720×1280, `test_dumps.py` with no problems for all 21 suites
  under `adb root` (the suite prompt roots before dumping; without it 12 suites report
  `Permission denied` and grading silently degrades to self-report).

Ratios are against `bare`. Full writeup in [`report.md`](report.md).

## Headline

ACU **1.10x** hybrid / **1.18x** acli. Perception tokens **0.67x** / **0.89x**. Billed input
(resident context integrated over turns, the quantity ACU tracks) **1.20x** / **1.23x** on the
median run. Tasks done 28.2 / 27.9 / 28.1 of ~30 — reliability parity for the fourth run running.

Against the previous run of the same matrix the ratios improved — ACU 1.30x → 1.10x, billed
1.63x → 1.20x — but **not because hybrid got cheaper**: hybrid 14.1 → 14.6 ACU, bare 10.8 → 13.3,
at unchanged completions (27.8 → 28.2 and 28.2 → 27.9 of ~30). The baseline moved, which is what a
baseline whose perception mode is re-chosen every run does. Perception is again **not** comparable
across runs — the bare arm went from 12.3 screenshots/run to a median of 12 with a 120-screenshot
tail and 4/12 runs doing genuine visual CUA. Quote the ratios from this run only against this
run's bare, never across archives.

## What this run found: a miss that costs two looks

`hd see --find PAT` answers a miss with

    # screen 720x1280, 0/103 nodes match 'Radian|Degree' (profile=views)
    # NO MATCH — re-run without --find (or --full) before concluding it's absent

— an instruction to spend another turn, and the arm obeyed it: **40 plain re-observations
directly follow a `--find` with no action in between**, across 12 hybrid runs (3.3/run), on top of
~7 `NO MATCH` prints per run. Turns are what ACU bills — hybrid spent 180 turns against bare's 158
for the same task list at 0.0795 ACU/turn — so a verb that answers "nothing, ask again" delivers
one look for the price of two.

The fix prints the compact tree on a miss, exactly as the <5-node case already auto-escalates, and
records it as a diff baseline because it *was* printed. `evals/test_find_nomatch.py` prices both
halves on the six matrix apps: **12 commands / 11,873 chars → 6 commands / 10,923 chars** — the
turn goes away and the characters do not double, because the tree replaces the follow-up `see`
rather than preceding it.

## Validity checks

* **Bare arm mode: mostly visual CUA.** 1/12 runs improvised tree tooling (≤5 screenshots), 4/12
  did visual CUA (≥20), 7 in between; median 12 screenshots. This is the *flattering* framing —
  the skill against visual computer use, the comparison the plugin README claims — not the harsh
  "skill vs. agent-improvised tree tooling" of the 2026-08-09 run. Perception ratios are not
  comparable to the earlier archives.
* **acli adoption: 12/12**, no cells dropped. 188 of 454 invocations went through a wrapper the
  agent defined (`A --llm-query`), counted by flag rather than by literal name.
* **Bypass: 7/12 hybrid, 7/12 bare, 4/12 acli** runs touched device state directly — no arm
  systematically skipped the UI, so the ACU comparison stands.
* **Collection complete:** every cell's last `context_growth_update` is within 3 iterations of its
  `iteration_stats` count. Command capture (`shell_process_started`) covers 96% / 91% / 81% of
  exec calls by arm, so command-derived counts are floors, and a lower floor for the arm that
  wrapped its tool.

One launch-side caveat worth carrying forward: `devin_session_create` for 36 cells overflows the
tool's output cap, so `gather.session_ids` saw 30 of 36 ids and the documented assert fired. The
cells were recovered by tag search (`devin_session_search tags=android-cua-eval`, filtered by
creation time) and every cell verified present before `runs.json` was written — the assert did its
job, but the snippet in `evals/README.md` cannot launch a matrix this size in one call without it.
