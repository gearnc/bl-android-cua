# Eval harness: android-hybrid-navigation vs. an unguided agent

A blinded A/B over long Android workflows. Each **cell** is one app × one arm × one replicate and
runs as its own child session, so ACU and perception tokens are attributable per cell.

- **hybrid** — child is told to use whatever tooling it has (the plugin is loaded).
- **bare** — child is forbidden from reading or invoking the skill.

Both arms get the *same* ~30-task suite and end with the same fixed `adb` state dump, so grading
does not depend on self-report.

## Requirements

An emulator snapshot with `~/start-emulator.sh`, Android 14 (API 34) at 720x1280 @320dpi, and the
suite's APKs preinstalled. The parent session needs the plugin loaded only if you intend to
re-measure `hd` itself with `test_detect.py` / `test_diff.py`.

## Running one

Standard shape — 6 apps (2 per UI toolkit) × 2 arms × 2 reps = 24 sessions:

```bash
python3 evals/plan.py                       # list the cells
python3 evals/plan.py --prompt markor|bare|1  # inspect one child's exact prompt
```

Launch (a `scripted_tools` snippet — tool calls must be inline, an imported module cannot make
them). 24 cells is under the org's 100-session cap, so this goes in one shot:

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

Then:

```bash
python3 evals/report.py        # tables to stdout
python3 evals/make_report.py > evals/data/report.md
```

Raw data lands in `evals/data/` (gitignored); set `EVAL_DATA=/path` to keep runs side by side.

## Reading the result honestly

Two checks that decide whether the numbers mean what they appear to:

1. **What is the bare arm doing?** Denied the skill, agents reinvent it — they write a
   `uiautomator dump` wrapper and grep it, typically within the first minute. When that happens
   the comparison is *skill vs. agent-improvised tree tooling*, not *skill vs. screenshots*.
   `screenshots` per bare run tells you which world you are in: ~2 means improvised tree tooling,
   dozens means real visual CUA. Expect a mix — in the 2026-08-09 run 5/12 bare runs were tree
   tooling and 2/12 were genuine visual CUA, and those two set the arm's tail.
2. **Is either arm bypassing the UI?** `bypass.py` counts `adb shell mkdir`-style state writes and
   deep-link intents. A lopsided count means one arm did less work, and the ACU comparison is void.

## Files

| file | role |
|---|---|
| `suites.py`, `phase2.py` | the 21 app suites: tasks, package, framework, verification dump |
| `plan.py` | matrix, session specs, structured-output schema |
| `gather.py` | response parsing for the collection snippets |
| `collect.py` | `context_growth_update` → per-run metrics |
| `bypass.py` | detects UI-bypassing shortcut commands |
| `report.py`, `make_report.py` | comparison tables and the markdown writeup |
| `test_detect.py` | framework-detection regression across all 21 apps |
| `test_diff.py` | bench: whole tree vs delta cost after real actions |
| `test_autodiff.py` | bench: what the DEFAULT `hd see` costs in the observe->act->observe loop, plus the turn-over and stale-baseline fallbacks |
| `test_dumps.py` | checks every suite's verification dump runs clean |
