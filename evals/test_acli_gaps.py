"""Bench: WHAT each observation tells the agent, not how big it is.

`accessibility-cli --llm` prints far less than `hd see` and the acli arm still cost 1.30x the
ACU of an agent handed nothing (2026-08-10 A/B/C). `test_acli.py` prices a look in characters;
this file prices it in *answers*, which is what decides whether the agent has to look again:

    nodes            how many elements the look mentions at all
    with coords      how many can be acted on without a second lookup
    with a label     how many can be named in a selector
    with state       how many report checked/selected, i.e. can verify a toggle task
    action selector  does `--click '[title=X]'` actually hit a button the tree just listed

The last row is the one that decides the run. A selector-only action API has to re-find the
node by string; when that misses, the agent falls back to raw coordinates, which is exactly
what the acli arm did (306 `--click` against 221 `--adb-tap` across 12 runs).

Usage: python3 evals/test_acli_gaps.py [app ...]
"""
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from env import ADB, ENV, find_acli, find_hd  # noqa: E402
from plan import DEFAULT_APPS  # noqa: E402
from suites import APPS  # noqa: E402

HD = ["python3", find_hd()]
ACLI = [find_acli(), "--platform", "android"]
COORD = re.compile(r"\((\d+),\s*(\d+)\)")
UNLABELED = re.compile(r"^\s*(Unknown|Button|Image|\*)\s*(\[value=\"[^\"]*\"\])?\s*[{:]")
ID_ATTR = re.compile(r"\[identifier=\"[^\"]*\"\]")
TEXT = re.compile(r"title=\"[^\"]|\"[^\"]")
HD_LINE = re.compile(r"^\s*\[(\d+)\]\s+(\S+)\s*(.*)$")
STATE = re.compile(r"checked=(true|false)|selected=(true|false)")


def run(cmd, timeout=180):
    t = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True, env=ENV, timeout=timeout)
    return r.returncode, r.stdout + r.stderr, time.time() - t


def launch(pkg):
    subprocess.run([ADB, "shell", "monkey", "-p", pkg, "-c",
                    "android.intent.category.LAUNCHER", "1"], capture_output=True, env=ENV)
    time.sleep(4)


def hd_facts(out):
    lines = [l for l in out.splitlines() if HD_LINE.match(l)]
    return dict(nodes=len(lines),
                coords=sum(1 for l in lines if COORD.search(l)),
                labeled=sum(1 for l in lines if '"' in l),
                stateful=sum(1 for l in lines if STATE.search(l)),
                anon=sum(1 for l in lines if '"' not in l),
                chars=len(out))


def acli_facts(out):
    """`--llm` prints `Button "NEXT" (x,y)`, `--llm-query` prints `Button[title="NEXT"]`; an
    `identifier=` is a resource id, not something the agent can read a screen off."""
    lines = [ID_ATTR.sub("", l) for l in out.splitlines()
             if l.strip() and not l.startswith("#") and "Connected to" not in l]
    return dict(nodes=len(lines),
                coords=sum(1 for l in lines if COORD.search(l)),
                labeled=sum(1 for l in lines if TEXT.search(l)),
                stateful=sum(1 for l in lines if STATE.search(l) or 'value="true"' in l
                             or 'value="false"' in l),
                anon=sum(1 for l in lines if UNLABELED.match(l)),
                chars=len(out))


def first_button(hd_out):
    """A labeled, clickable node the agent could plausibly aim at, as (index, label)."""
    for l in hd_out.splitlines():
        m = HD_LINE.match(l)
        if m and "<C" in l and '"' in l:
            return int(m.group(1)), l.split('"')[1]
    return None, None


def test_acli_still_omits_state():
    """The claim this file rests on: acli's compact view is interactive-only.

    If a later accessibility-cli starts printing labels and state, this assertion fails and the
    conclusion in `run-2026-08-10-acli/README.md` has to be re-derived rather than quoted.
    """
    launch(APPS["markor"]["pkg"])
    _, llm, _ = run(ACLI + ["--llm"])
    _, hd_out, _ = run(HD + ["see", "--no-diff"])
    assert hd_facts(hd_out)["nodes"] > acli_facts(llm)["nodes"], \
        "accessibility-cli --llm no longer prints fewer nodes than hd see"


if __name__ == "__main__":
    which = sys.argv[1:] or list(DEFAULT_APPS)
    hdr = (f"{'app':<10}{'tool':<12}{'nodes':>6}{'coords':>7}{'label':>6}{'state':>6}"
           f"{'anon':>6}{'chars':>7}{'secs':>6}")
    print(hdr)
    hits = misses = 0
    for key in which:
        launch(APPS[key]["pkg"])
        _, hd_out, t_hd = run(HD + ["see", "--no-diff"])
        _, llm, t_llm = run(ACLI + ["--llm"])
        _, tree, t_tree = run(ACLI + ["--llm-query"])
        for name, facts, secs in (("hd see", hd_facts(hd_out), t_hd),
                                  ("acli --llm", acli_facts(llm), t_llm),
                                  ("acli --query", acli_facts(tree), t_tree)):
            print(f"{key:<10}{name:<12}{facts['nodes']:>6}{facts['coords']:>7}"
                  f"{facts['labeled']:>6}{facts['stateful']:>6}{facts['anon']:>6}"
                  f"{facts['chars']:>7}{secs:>6.1f}")
        idx, label = first_button(hd_out)
        if label:
            rc, out, secs = run(ACLI + ["--click", f"[title={label}]", "--timeout", "3000"])
            ok = rc == 0 and "not found" not in out.lower() and "error" not in out.lower()
            hits += ok
            misses += not ok
            print(f"{key:<10}{'  --click':<12} [title={label}] -> "
                  f"{'hit' if ok else 'MISS'} in {secs:.1f}s   (hd tap {idx} would take it "
                  f"straight off the tree)")
    if hits + misses:
        print(f"\nselector actions: {hits} hit, {misses} missed of {hits + misses} — every miss "
              "is a fallback to raw coordinates, which is a look the tree already paid for")
