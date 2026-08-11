"""Poll every cell once (concurrency 2, ~1.5s pacing) and merge into data/state.json.

Never let a throttled/errored read (acu=0) overwrite a good cached reading.
Run via scripted_tools; call_tool must stay in the inline snippet, so this file only
holds the pure merge logic.
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gather import status, task_counts  # noqa: E402
from paths import DATA  # noqa: E402

STATE = os.path.join(DATA, "state.json")


def load():
    return json.load(open(STATE)) if os.path.exists(STATE) else {}


def merge(state, cell, get_output):
    """Merge one `get` response, refusing to downgrade a good reading with an error read."""
    s = status(get_output)
    if s["acu"] == 0.0 and cell in state and state[cell].get("acu", 0) > 0:
        state[cell]["stale_read"] = state[cell].get("stale_read", 0) + 1
        return state[cell]
    s.update(task_counts(get_output))
    state[cell] = s
    return s


def save(state):
    json.dump(state, open(STATE, "w"), indent=1)


SETTLED = ("waiting_for_user", "inactivity")   # a finished cell parks, then its VM suspends


def settled(v):
    """Finished, with something to collect.

    A cell left parked long enough suspends on `inactivity`: still done, still holding its
    structured output. Waiting for `waiting_for_user` alone makes a completed matrix look like
    it regressed to 0/36 as the sessions age out.
    """
    return v["detail"] in SETTLED and v["has_output"]


def summarize(state):
    done = [c for c, v in state.items() if settled(v)]
    parked = [c for c, v in state.items() if v["detail"] in SETTLED]
    acu = sum(v.get("acu", 0) for v in state.values())
    return (f"{len(done)}/{len(state)} with structured output, {len(parked)} settled, "
            f"{acu:.1f} ACU total")
