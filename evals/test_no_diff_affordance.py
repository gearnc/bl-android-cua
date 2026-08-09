"""Bench + regression: the delta default is only worth what agents let it be worth.

The 2026-08-09 auto-diff run made the delta the default and still measured almost no deltas: of
the 12 hybrid runs, agents typed `hd see --no-diff` 717 times and the delta path printed 15
times. The mechanism was not the diff, it was the affordance — `--no-diff` had its own line in
the verb list, its own sentence in SKILL.md, and was named in the header of every delta, so the
agent learned the escape hatch before it ever saw a delta (in every run the first `--no-diff`
predates the first delta output).

This file guards the affordance and prices what it cost:

  * `test_not_advertised` — the flag still works, but nothing in the CLI usage, the runtime
    output, or SKILL.md's core loop offers it. A regression here re-opens the 717-call habit.
  * running the module measures, over real observe->act->observe loops, what one `--no-diff`
    re-read costs against the default delta, and projects that over the run's 717 uses.
"""

import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from env import ENV, find_hd  # noqa: E402
from test_diff import measure  # noqa: E402

HD_PATH = Path(find_hd())
SKILL = HD_PATH.parent / "SKILL.md"

# From evals/run-2026-08-09-autodiff/: `--no-diff` calls and deltas printed, over 12 hybrid runs.
NO_DIFF_USES = 717
DELTAS_PRINTED = 15
CHARS_PER_TOKEN = 4  # the ratio the harness's own approx_ant_tokens uses


def usage_text():
    r = subprocess.run(["python3", str(HD_PATH)], capture_output=True, text=True, env=ENV)
    return r.stdout + r.stderr


def test_not_advertised():
    """The opt-out must remain accepted and remain unmentioned."""
    src = HD_PATH.read_text()
    assert '"--no-diff" not in a' in src, "the escape hatch must keep working for scripts"

    usage = usage_text()
    assert "hd see" in usage, "usage did not print"
    assert "--no-diff" not in usage, "usage advertises --no-diff again"

    # The delta header is printed hundreds of times per run; naming the flag there taught it.
    header = re.search(r'f"# screen \{size\[0\]\}x\{size\[1\]\}, \+\{len\(added\)\}.*?\)\)',
                       src, re.S)
    assert header and "--no-diff" not in header.group(0), "the delta header names --no-diff"

    loop = SKILL.read_text().split("## Earned shortcuts")[0]
    assert "--no-diff" not in loop, "SKILL.md's core loop offers --no-diff"


if __name__ == "__main__":
    from suites import APPS  # noqa: E402

    test_not_advertised()
    print("affordance: --no-diff accepted, advertised nowhere  OK\n")

    which = sys.argv[1:] or ["markor", "amaze", "seal", "unitto"]
    tot_full = tot_diff = n = 0
    for key in which:
        try:
            rows = measure(APPS[key]["pkg"])
        except Exception as e:                                   # noqa: BLE001
            print(f"{key}: FAILED {e}")
            continue
        for act, full, delta, turned in rows:
            tot_full += full
            tot_diff += delta
            n += 1
            note = " (screen turned over -> whole tree)" if turned else ""
            print(f"{key:<10}{act:<10} --no-diff={full:>6}  default={delta:>6}  "
                  f"saved={1 - delta / full:>6.0%}{note}")
    if n:
        per_call = (tot_full - tot_diff) / n / CHARS_PER_TOKEN
        print(f"\nTOTAL over {n} re-observations: --no-diff={tot_full} default={tot_diff} "
              f"saved={1 - tot_diff / tot_full:.0%} ({per_call:,.0f} tokens per re-observation)")
        # An upper bound, not a forecast: some of those 717 calls were on screens that turned
        # over, where the default prints the whole tree anyway and saves nothing.
        print(f"Upper bound over the run's {NO_DIFF_USES} `--no-diff` calls "
              f"({DELTAS_PRINTED} deltas printed): <={per_call * NO_DIFF_USES / 12:,.0f} "
              f"perception tokens per hybrid run, against a measured mean of 33,609.")
        assert tot_diff <= tot_full, "the default observation is more expensive than --no-diff"
