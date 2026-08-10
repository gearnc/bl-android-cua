# Eval harness: android-hybrid-navigation vs. an unguided agent vs. accessibility-cli

A blinded A/B/C over long Android workflows. Each **cell** is one app × one arm × one replicate
and runs as its own child session, so ACU and perception tokens are attributable per cell.

- **hybrid** — child is told to use whatever tooling it has (the plugin is loaded).
- **bare** — child is forbidden from reading or invoking the skill. The baseline every ratio is
  taken against, because it is the only arm handed nothing.
- **acli** — skill forbidden, and the child is pointed at
  [DioxusLabs/accessibility-cli](https://github.com/DioxusLabs/accessibility-cli), prebuilt into
  the snapshot and on `PATH`.

Every arm gets the *same* ~30-task suite and ends with the same fixed `adb` state dump, so grading
does not depend on self-report, and the arms differ by exactly one paragraph (`ARM_*` in
`suites.py`).

## Requirements

An emulator snapshot with `~/start-emulator.sh`, Android 14 (API 34) at 720x1280 @320dpi, the
suite's APKs preinstalled, and `accessibility-cli` on `PATH` (the org blueprint clones
`~/repos/accessibility-cli` and `cargo install`s it; it needs a Rust with edition 2024 support and
`libdbus-1-dev libatspi2.0-dev libx11-xcb-dev`). The parent session needs the plugin loaded only
if you intend to re-measure `hd` itself with `test_detect.py` / `test_diff.py` / `test_acli.py`.

## Running one

Standard shape — 6 apps (2 per UI toolkit) × 3 arms × 2 reps = 36 sessions:

```bash
python3 evals/plan.py                          # list the cells
python3 evals/plan.py --arms hybrid,bare       # drop the accessibility-cli arm
python3 evals/plan.py --prompt markor|acli|1   # inspect one child's exact prompt
```

Launch (a `scripted_tools` snippet — tool calls must be inline, an imported module cannot make
them). 36 cells is under the org's 100-session cap, so this goes in one shot:

```python
import json, sys
sys.path.insert(0, "/home/ubuntu/repos/bl-android-cua/evals")
from plan import cells, spec, SCHEMA
from gather import session_ids
from paths import RUNS
from devin_tools import call_tool

async def main():
    ks = cells(reps=2)
    out = await call_tool("devin_mcp", {"command": "call_tool",
        "tool_name": "devin_session_create",
        "tool_args": {"sessions": [spec(k) for k in ks], "devin_mode": "normal",
                      "structured_output_schema": SCHEMA}})
    ids = session_ids(out)
    assert len(ids) == len(ks), f"{len(ids)} ids for {len(ks)} cells — refusing to mislabel"
    json.dump(dict(zip(ks, ids)), open(RUNS, "w"), indent=1)
asyncio.run(main())
```

Poll with `devin_session_interact action=get` and `gather.status`. Children park in
`waiting_for_user` when done, which still holds a concurrency slot — put them to sleep
(`action=sleep`) if you are running a matrix large enough to hit the cap.

## Collecting

Per cell, in one pass (see the playbook for the full snippet):

| what | where it comes from |
|---|---|
| ACU, completion state | `devin_session_interact action=get` → `gather.status` |
| n_done / n_partial / n_failed | same response → `gather.task_counts` |
| perception tokens, screenshots, iterations | last `context_growth_update` event → `gather.growth` → `collect.metrics` |
| shortcut commands | all `shell_process_started` events → `gather.exec_commands` → `bypass.classify` |

**Paginate with `first=gather.PAGE` (40), never 100.** A 100-event page overflows the tool's
output cap on a busy session: it is cut off mid-list but keeps its "More results" cursor, so the
loop walks on and drops the tail of every page — no error, just fewer events. What you then take
for the *last* growth event is a mid-run one, and every number derived from it is censored at a
different iteration in every cell. In the 2026-08-10 run that clipped `amaze|bare|1` at turn 69
of 243 and reported 11k perception tokens against an actual 38k, while the cells it happened to
spare read correctly — i.e. it biases the comparison, it does not just add noise.
`gather.event_ids`/`exec_commands` now raise on a truncated page; halve `first` and refetch the
same cursor. Cross-check before trusting a collection: the last growth event's `iteration_count`
should be within a few turns of the last `iteration_stats` event's `iteration`.

Then:

```bash
python3 evals/report.py        # tables to stdout
python3 evals/make_report.py > evals/data/report.md
```

Raw data lands in `evals/data/` (gitignored); set `EVAL_DATA=/path` to keep runs side by side.

## Reading the result honestly

Checks that decide whether the numbers mean what they appear to:

1. **What is the bare arm doing?** Denied the skill, agents reinvent it — they write a
   `uiautomator dump` wrapper and grep it, typically within the first minute. When that happens
   the comparison is *skill vs. agent-improvised tree tooling*, not *skill vs. screenshots*.
   `screenshots` per bare run tells you which world you are in: ~2 means improvised tree tooling,
   dozens means real visual CUA. Expect a mix, and expect it to move between runs of the same
   matrix: 5/12 tree tooling vs 2/12 visual CUA in the 2026-08-09 run, then 2/12 vs 6/12 in the
   2026-08-09-autodiff re-run hours later. `make_report.py` derives the sentence from the
   screenshot distribution rather than asserting it; don't quote a perception ratio across two
   runs whose bare arms did different things.
2. **Is a perception ratio being read as a cost ratio?** It is not one. Billed input is the
   resident context integrated over turns (`billed.py`), so cheap looks that persist can cost
   more than expensive looks that don't: in the 2026-08-09 run hybrid spent 0.50x the perception
   tokens and billed the same (median 3.23 vs 3.18 Mtok). Quote perception ratios as perception,
   and compute billed tokens before claiming a cost win. A whole run's perception spend is a
   fraction of a percent of what it bills.
3. **Did the arm use the cheap verb at all?** A saving nobody types is worth nothing, and this
   has now cost two runs in a row: `--diff` went untyped, then `--no-diff` opted out of the
   default 717 times against 15 deltas actually printed. `make_report.py` prints the hybrid
   arm's observation-verb mix; read it before crediting or blaming a mechanism.
4. **Did the acli arm type `accessibility-cli` at all?** Same question as (3), one arm over:
   `make_report.py` prints the invocation mix and names any acli run that never invoked the
   binary. Those cells measured the agent's own fallback and have to come out before quoting an
   acli ratio. Run `python3 evals/test_acli.py` before the matrix — a binary that errors on this
   snapshot guarantees the fallback. It also prices one observation each way; on the six default
   apps `accessibility-cli --llm` printed 29-749 chars against `hd see`'s 154-2684, because it
   emits only nodes it considers interactive, so a cheaper look here is not yet a cheaper run —
   it may be one that has to look again.
5. **Is the collection complete?** Compare each cell's `iterations` against the last
   `iteration_stats` event; a cell whose growth series stops early is censored, not cheap (see
   the pagination note above).
6. **Is either arm bypassing the UI?** `bypass.py` counts `adb shell mkdir`-style state writes and
   deep-link intents. A lopsided count means one arm did less work, and the ACU comparison is void.

## Files

| file | role |
|---|---|
| `suites.py`, `phase2.py` | the 21 app suites: tasks, package, framework, verification dump |
| `plan.py` | matrix, session specs, structured-output schema |
| `gather.py` | response parsing for the collection snippets |
| `collect.py` | `context_growth_update` → per-run metrics |
| `billed.py` | the same events → billed input tokens (context integrated over turns), which is what ACU actually charges |
| `bypass.py` | detects UI-bypassing shortcut commands |
| `make_report.py` "Where the ACU goes" | looks/task, actions per look, blind batches, ACU/turn — why a cheaper look can still be a dearer run |
| `report.py`, `make_report.py` | comparison tables and the markdown writeup |
| `test_detect.py` | framework-detection regression across all 21 apps |
| `test_diff.py` | bench: whole tree vs delta cost after real actions |
| `test_autodiff.py` | bench: what the DEFAULT `hd see` costs in the observe->act->observe loop, plus the turn-over and stale-baseline fallbacks |
| `test_no_diff_affordance.py` | bench + regression: `--no-diff` still works but is advertised nowhere, and what one `--no-diff` re-read costs against the default delta |
| `test_find_baseline.py` | bench + regression: a `--find` between two `see`s must not cost the whole tree (set `HD_PY_OLD=` to price it against another revision) |
| `test_toggle_state.py` | regression: a checkable node must render its `checked=` state (set `HD_PY=` to run it against another revision) |
| `test_capture_retrieval.py` | bench: `hd see -q` + `hd find` (capture once, print only matches) vs printing the tree — cost *and* recall, since cheaper retrieval that misses nodes is not cheaper |
| `test_dumps.py` | checks every suite's verification dump runs clean |
| `test_acli.py` | smoke test + bench: `accessibility-cli` observation cost vs `hd see`, per app |
| `test_acli_gaps.py` | bench: what an `accessibility-cli` look *answers* (nodes, coordinates, labels, state) vs `hd see`, and whether its selector actions hit |
| `test_act_see.py` | bench + regression: `-s` folds the post-action look into the action verb, halving the commands an act-then-observe cycle costs |
