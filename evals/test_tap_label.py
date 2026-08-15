"""Bench + regression: tapping a node you can already name must not cost a look.

An index is a fact about a rendering, so before `hd tap PAT` the only way to learn one was to
buy an observation. The 2026-08-15 A/B/C priced that: over 12 hybrid runs, 236 commands were a
look with no action in them, and 115 of those — in all 12 runs — were followed immediately by
nothing but `hd tap <index>`. The look existed to turn a label the agent already knew ("Save",
"New note") into a number. The acli arm never paid it: it typed `--click '[title=Save]'` 150
times and let its tool do the resolution.

Two things are measured, because either alone would be misleading:

  * turns and bytes — `hd see --find PAT; hd tap <i>` against `hd tap PAT`, which is the whole
    saving: one turn instead of two;
  * identity — the pattern form must land on the SAME node the index form did, or it is buying
    turns with wrong taps. Every target here is resolved both ways and the tapped coordinates
    compared.

Plus the ambiguity guard: a pattern matching several distinct nodes must tap nothing and print
the candidates with their indexes, so disambiguating still costs no extra look.

    python3 evals/test_tap_label.py [app ...]

`$HD_PY` selects the revision under test.
"""
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from env import ADB, ENV, find_hd  # noqa: E402
from test_diff import launch  # noqa: E402

HD = ["python3", find_hd()]
# A clickable row names itself either with its own label or, on Compose, with the near:"..."
# hint adopt_labels gave it - the only handle that screen offers, and the one an agent reads.
ROW = re.compile(r'^\s*\[(\d+)\](?=.*<C).*?(?:near:)?"((?:[^"\\]|\\.)+)"')
TAPPED = re.compile(r"at \((\d+),(\d+)\)")


def hd(*args):
    r = subprocess.run(HD + list(args), capture_output=True, text=True, env=ENV)
    return r.stdout + r.stderr, r.returncode


def restart(pkg):
    """Both idioms have to resolve their label against the SAME screen, so each trial starts cold.

    `monkey` alone resumes whatever screen the previous trial left behind - on Joplin that is a
    different toolbar, and the two idioms then match against two different trees, which measures
    the app's state restoration rather than the verb.
    """
    subprocess.run([ADB, "shell", "am", "force-stop", pkg], capture_output=True, env=ENV)
    time.sleep(1)
    launch(pkg)


def targets(tree, n=3):
    """Labels that name exactly one clickable row: what an agent knows before it looks."""
    rows = [(int(m.group(1)), m.group(2)) for ln in tree.splitlines()
            if (m := ROW.match(ln))]
    seen = [lab for _, lab in rows]
    out = []
    for idx, label in rows:
        pat = re.escape(label)
        if seen.count(label) == 1 and len(label) > 2 and label.isascii():
            out.append((idx, label, pat))
        if len(out) == n:
            break
    return out


def where(out):
    m = TAPPED.search(out)
    return (int(m.group(1)), int(m.group(2))) if m else None


def old_way(pat):
    """What the run is full of: a look to resolve the label, then a tap on the index it gave."""
    look, _ = hd("see", "--find", pat)
    # An agent reading the hits takes the clickable one - a label sits on a Text node that is not
    # itself the target on Compose, and taking the first row regardless would compare against a
    # worse idiom than the run actually used.
    rows = [ln for ln in look.splitlines() if ln.strip().startswith("[")]
    pick = next((ln for ln in rows if "<C" in ln), rows[0] if rows else None)
    m = re.match(r"^\s*\[(\d+)\]", pick) if pick else None
    if not m:
        return None, len(look), 2
    act, _ = hd("tap", m.group(1), "-n")
    return where(act), len(look) + len(act), 2


def new_way(pat):
    act, rc = hd("tap", pat, "-n")
    return where(act), len(act), 1, rc


def compare(app, pkg):
    restart(pkg)
    tree, _ = hd("see", "--full", "--no-diff")
    rows = []
    for _, label, pat in targets(tree):
        restart(pkg)
        hd("see", "-q")
        old_at, old_bytes, old_cmds = old_way(pat)
        restart(pkg)
        hd("see", "-q")
        new_at, new_bytes, new_cmds, rc = new_way(pat)
        rows.append(dict(label=label, old=old_bytes, new=new_bytes,
                         old_cmds=old_cmds, new_cmds=new_cmds,
                         old_at=old_at, new_at=new_at, refused=rc != 0))
        time.sleep(0.5)
    return rows


def test_ambiguity_is_reported_not_guessed():
    """`.` matches every row: the verb must refuse, and hand back indexes to choose from."""
    out, rc = hd("tap", ".", "-n")
    assert rc != 0, "a pattern matching the whole tree tapped something anyway"
    assert "matches" in out and re.search(r"^\s*\[\d+\]", out, re.M), \
        f"ambiguity was not answered with candidate indexes:\n{out[:400]}"


def test_a_miss_prints_the_tree_once():
    out, rc = hd("tap", "zzz-no-such-node-zzz", "-n")
    assert rc != 0, "a pattern matching nothing reported success"
    assert re.search(r"^\s*\[\d+\]", out, re.M), \
        f"a miss did not print the tree it matched against:\n{out[:400]}"


def test_pattern_form_exists():
    src = Path(find_hd()).read_text()
    assert "def tap_pattern" in src, "no pattern form of tap"
    assert "a[1].isdigit()" in src, "`hd tap` does not dispatch on index vs pattern"


if __name__ == "__main__":
    from suites import APPS  # noqa: E402

    which = sys.argv[1:] or ["markor", "amaze", "seal", "unitto", "joplin", "lesspass"]
    launch(APPS[which[0]]["pkg"])
    hd("see", "-q")
    test_pattern_form_exists()
    test_ambiguity_is_reported_not_guessed()
    test_a_miss_prints_the_tree_once()
    print("regression: pattern form dispatches, refuses ambiguity, prints a miss once  OK\n")

    n = same = refused = 0
    t_old = t_new = c_old = c_new = 0
    for app in which:
        try:
            rows = compare(app, APPS[app]["pkg"])
        except Exception as e:                                   # noqa: BLE001
            print(f"{app}: FAILED {e}")
            continue
        for r in rows:
            n += 1
            hit = r["old_at"] is not None and r["old_at"] == r["new_at"]
            same += hit
            refused += r["refused"]
            if not r["refused"]:
                t_old += r["old"]
                t_new += r["new"]
                c_old += r["old_cmds"]
                c_new += r["new_cmds"]
            verdict = "" if hit else ("  refused (ambiguous)" if r["refused"] else "  MISMATCH")
            print(f"{app:<10}{r['label'][:24]:<26} see --find + tap = {r['old_cmds']} cmds "
                  f"{r['old']:>5}b {str(r['old_at']):<12} -> tap PAT = {r['new_cmds']} cmd "
                  f"{r['new']:>5}b {str(r['new_at']):<12}{verdict}")
            # A refusal is a design choice, not a saving: it keeps its candidates out of the
            # ratio above. A tap that landed somewhere ELSE is a bug and fails the bench.
            assert hit or r["refused"], \
                f"{app}/{r['label']}: pattern tapped {r['new_at']}, index tapped {r['old_at']}"
    if n:
        print(f"\nTOTAL {n} targets over {len(which)} apps, "
              f"{n - refused} resolved / {refused} refused as ambiguous:")
        print(f"  commands  {c_old} -> {c_new}  ({1 - c_new / c_old:.0%} fewer turns)")
        print(f"  printed   {t_old}b -> {t_new}b  ({1 - t_new / t_old:.0%} fewer bytes)")
        print(f"  same node {same}/{n - refused} resolved")
        assert same == n - refused, "the pattern form did not land where the index form did"
