# Run, 2026-08-10 (second) — 36 cells, three arms, plugin `main` @ f90a4b9

Same matrix as [`run-2026-08-10-acli`](../run-2026-08-10-acli/) — 6 apps × 2 replicates × 3 arms,
~30 machine-verifiable tasks each, Normal capability, fixed `adb` verification dump — re-run
against the plugin revision that shipped the two fixes that run asked for: per-rendering diff
baselines (#7) and the `-s` act-then-look fold (#8).

| arm | prompt paragraph | what it had |
|---|---|---|
| `hybrid` | `ARM_HYBRID` | whatever tooling it has, i.e. the skill |
| `bare` | `ARM_BARE` | the skill denied, nothing offered instead |
| `acli` | `ARM_ACLI` | the skill denied, pointed at `accessibility-cli` |

Measured revisions, verified before launch:

* plugin `main` @ `f90a4b9`, confirmed in a throwaway child's plugin cache (the `-s` verb from
  #8 present) rather than assumed from the snapshot date;
* `accessibility-cli` `0.1.0` @ `03cfeb3` (DioxusLabs/accessibility-cli), on `PATH` in the child
  snapshot, `test_acli.py` `problems=none` for all six apps;
* emulator Android 14 / API 34 at 720×1280; `test_dumps.py` `rc=0` for all six matrix apps
  (`markor amaze seal unitto joplin lesspass`). Four apps outside this matrix
  (`material_files`, `tasks_org`, `breezy_weather`, `blacksquircle`) return `rc=1` on this
  snapshot; they are not in the suite and were not launched.

Ratios are against `bare`. Full writeup in [`report.md`](report.md).

## Headline

ACU **1.30x** hybrid / **1.32x** acli. Perception tokens **0.96x** / **1.24x**. Billed input
(resident context integrated over turns, the quantity ACU tracks) **1.63x** / **1.28x** on the
median run. Tasks done 27.8 / 28.2 / 27.9 of ~30 — reliability parity again, no arm buying its
cost back in completions.

Against the previous run of the same matrix, hybrid moved the wrong way: ACU 1.13x → 1.30x and
perception 0.74x → 0.96x. Both arms changed, so read the absolutes: hybrid 13.0 → 14.1 ACU,
bare 11.5 → 10.8. Perception is **not** comparable across the two runs — the bare arm's mode
moved (19.4 screenshots per run then, 12.3 now).

## What this run found: a delta against a tree nobody read

`hd see --find PAT` renders the whole tree (indexes must stay valid for `hd tap`) and prints only
the matching lines; `hd see -q` prints nothing. #7 made both of them *record that tree as the diff
baseline*. So the sequence agents actually type —

    hd tap 5            # screen changes
    hd see --find Save  # prints one line
    hd see              # "what am I looking at?"

— answers `# no change since the last see`, about a screen the agent has never been shown. It is
silent and it is the common path: `--find` is 62% of the hybrid arm's 1,016 observation calls, and
157 of the 287 plain re-observations (55%) directly follow a `--find`/`-q`.

`evals/test_seen_baseline.py` measures information rather than brevity — how many nodes of the
screen now in front of the agent have never been printed to it — and on 11 re-observations over
4 apps scores the shipped revision **48 unseen nodes**, the fix **0**, for +2,845 chars (~65
tokens per re-observation). The older bench (`test_find_baseline.py`) counts deltas printed, so it
scores the broken revision *better*: that is how the regression shipped.

The fix records a baseline only for a rendering that was printed.

## Validity checks

* **Bare arm mode: mixed.** 3/12 runs improvised tree tooling (≤5 screenshots), 2/12 did visual
  CUA (≥20), 7 in between; median 12 screenshots. Not the "skill vs. improvised tree tooling"
  framing of the previous run, and not screenshot CUA either — perception ratios are not
  comparable to the earlier archives.
* **acli adoption: 12/12**, no cells dropped. 294 of 709 invocations went through a wrapper the
  agent defined (`A --llm-query`), counted by flag, not by literal name.
* **Bypass: 6/12 hybrid, 5/12 bare, 4/12 acli** runs touched device state directly — no arm
  systematically skipped the UI.
* **Collection complete:** every cell's last `context_growth_update` is within 3 iterations of
  its last `iteration_stats` event. Command capture (`shell_process_started`) covers 96%/90%/82%
  of exec calls by arm, so command-derived counts are floors.

Collecting this run also found a *second* silent truncation in the events API, independent of the
`first=100` one that voided the first collection of the previous run: `action=details` clips each
content field at ~2k chars unless `max_content_length` is passed, with no notice and no overflow
file, dropping the `current_context_tokens` at the tail of exactly the busiest cells. See
`evals/README.md` and `evals/collect_events.py`.
