"""Bench: capture-then-retrieve (`hd see -q; hd find PAT`) vs printing the tree.

Why this verb exists. In the 2026-08-09 run the bare arm, denied the skill, always rebuilt the
same tool with one difference: it separated capture from retrieval. It dumped the tree to a file
(10.2 raw dumps per run, costing nothing because nothing was printed) and grepped it (6.0
filtered reads), so only matching lines were ever billed. `hd see` fused the two — every
observation rendered a tree into the transcript — and that is the whole of hybrid's residual
text cost: 9.7k vs 7.8k exec tokens per run at the median, which after residency (a token added
at turn i is re-read at every later turn) is the ~3% billed gap between the arms.

`hd see -q` caches the FULL tree and prints one header line; `hd find PAT` greps the cache with
no adb round-trip. Two things are measured here, because either alone would be misleading:

  * cost — printed bytes for locate-a-target, against `hd see` and `hd see --find`;
  * recall — `hd find` must return everything `hd see --find` would, or it is buying tokens
    with missed nodes. Quiet capture stores the full tree precisely so it cannot lose recall.
"""

import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from env import ENV, find_hd  # noqa: E402
from test_diff import launch  # noqa: E402

HD = ["python3", find_hd()]

# Targets a task would plausibly look for, per app.
TARGETS = {"markor": ["Settings|More", "todo|Todo"],
           "amaze": ["torage|ile", "Search"],
           "seal": ["Settings", "Download"],
           "unitto": ["Settings|menu", "Converter|Calculator"],
           "joplin": ["New|note", "Settings|Configuration"],
           "lesspass": ["Site|site", "Password|password"]}

# The header a cheap observation still pays: "# screen ... N nodes ..." plus the match line.
HEADERS = 2


def hd(*args):
    return subprocess.run(HD + list(args), capture_output=True, text=True, env=ENV).stdout


def hits(out):
    """Node lines in an observation's output, ignoring the `#` header lines."""
    return {ln.strip() for ln in out.splitlines() if ln.strip().startswith("[")}


def compare(app, pkg):
    launch(pkg)
    rows = []
    for pat in TARGETS[app]:
        tree = hd("see", "--no-diff")                     # print the screen and read it
        direct = hd("see", "--find", pat)                 # today's cheap path: dump + print hits
        quiet = hd("see", "-q")                           # capture, print nothing
        cached = hd("find", pat)                          # retrieve, print only hits
        missed = hits(direct) - hits(cached)
        rows.append(dict(pat=pat,
                         tree=len(tree), direct=len(direct),
                         split=len(quiet) + len(cached),
                         n_direct=len(hits(direct)), n_cached=len(hits(cached)),
                         missed=missed))
        time.sleep(0.5)
    return rows


def loop_cost(app, pkg, n=3):
    """The realistic sequence: observe, locate, act, observe again — old way vs new way."""
    launch(pkg)
    pat = TARGETS[app][0]
    old = new = 0
    for _ in range(n):
        old += len(hd("see", "--no-diff")) + len(hd("see", "--find", pat))
        new += len(hd("see", "-q")) + len(hd("find", pat))
        # `-n`: only the observation verbs are being priced here.
        subprocess.run(HD + ["key", "back", "-n"], capture_output=True, env=ENV)
        time.sleep(1)
    return old, new


def multi_check(app, pkg):
    """Several checks on ONE screen: the case the split verb is actually for.

    Bytes are close to `see --find` per lookup either way; what the cache removes is a
    `uiautomator dump` per lookup, which is wall-clock (infra cost), not tokens.
    """
    launch(pkg)
    pats = TARGETS[app] + ["<C>"]
    t0 = time.time()
    old = sum(len(hd("see", "--find", p)) for p in pats)
    t_old = time.time() - t0
    t0 = time.time()
    new = len(hd("see", "-q")) + sum(len(hd("find", p)) for p in pats)
    t_new = time.time() - t0
    return old, new, t_old, t_new


if __name__ == "__main__":
    which = sys.argv[1:] or ["markor", "amaze", "seal", "unitto"]
    from suites import APPS  # noqa: E402

    t_tree = t_direct = t_split = 0
    for app in which:
        try:
            rows = compare(app, APPS[app]["pkg"])
        except Exception as e:                                   # noqa: BLE001
            print(f"{app}: FAILED {e}")
            continue
        for r in rows:
            t_tree += r["tree"]
            t_direct += r["direct"]
            t_split += r["split"]
            print(f"{app:<10}{r['pat']:<22} tree={r['tree']:>6}  "
                  f"see --find={r['direct']:>5} ({r['n_direct']} hits)  "
                  f"see -q + find={r['split']:>5} ({r['n_cached']} hits)  "
                  f"vs tree={1 - r['split'] / r['tree']:>5.0%}")
            assert not r["missed"], (
                f"{app}/{r['pat']}: cached retrieval missed nodes that --find returned: "
                f"{sorted(r['missed'])[:3]}")
    if t_tree:
        print(f"\nTOTAL printed bytes: tree={t_tree}  see --find={t_direct}  "
              f"see -q + find={t_split}")
        print(f"  vs printing the tree: {1 - t_split / t_tree:.0%} cheaper")
        print(f"  vs `see --find`:      {1 - t_split / t_direct:+.0%} "
              "(the header is the price of caching a full tree)")
    print()
    for app in which[:2]:
        old, new = loop_cost(app, APPS[app]["pkg"])
        print(f"{app:<10} observe+locate x3: was={old:>6} now={new:>6} "
              f"saved={1 - new / old:.0%}")
    print()
    for app in which[:2]:
        old, new, t_old, t_new = multi_check(app, APPS[app]["pkg"])
        print(f"{app:<10} 3 checks on one screen: bytes {old}->{new} "
              f"({1 - new / old:+.0%}), wall {t_old:.1f}s->{t_new:.1f}s "
              f"({1 - t_new / t_old:+.0%})")
