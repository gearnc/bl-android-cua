"""Bench + regression: `hd tap N` must tap node N, even when the screen has look-alikes.

Before acting, `hd tap` re-dumps and re-finds the node by (class, text, desc, id) to catch a
layout that shifted under the caller. On a form that guard misfires: the fields of an RN form
share one resource-id and are all empty, so every one of them has the SAME identity, the search
returns the first, and the tap lands on the row above the one the caller indexed — announced as
`# node moved; tapping fresh coords`, which reads like the guard working. It fired 17 times
across the 12 hybrid runs of the 2026-08-12 A/B/C.

The index IS the disambiguator when the identity is not unique, so this bench checks the only
thing that matters: after `hd tap k -n; hd type ...`, which field ended up holding the text.

    python3 evals/test_tap_identity.py [app ...]

`$HD_PY` selects the revision under test, `$HD_PY_OLD` the one to compare against.
"""
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from env import ADB, ENV, find_hd  # noqa: E402
from test_diff import launch  # noqa: E402
from test_replace import fields, run  # noqa: E402
from test_seen_baseline import old_revision  # noqa: E402


def reset(pkg):
    """A pristine form: identical empty fields are the case under test."""
    subprocess.run([ADB, "shell", "pm", "clear", pkg], capture_output=True, env=ENV)
    launch(pkg)
    time.sleep(2)


def lands_on_indexed_field(hd_py, pkg):
    """Type a marker into each field by index; return how many landed where they were aimed."""
    hit = 0
    found = fields(run("see", "--full", "--no-diff", hd_py=hd_py))
    for k, (idx, _) in enumerate(found[:3]):
        reset(pkg)
        found = fields(run("see", "--full", "--no-diff", hd_py=hd_py))
        if k >= len(found):
            break
        run("tap", str(found[k][0]), "-n", hd_py=hd_py)
        run("type", "marker", "-n", hd_py=hd_py)
        time.sleep(1)
        after = fields(run("see", "--full", "--no-diff", hd_py=hd_py))
        # Which field stopped being empty — a password field renders bullets, not the marker,
        # and the form's numeric fields (length/counter) start out filled.
        holder = [i for i, (_, text) in enumerate(after)
                  if text and not text.isdigit() and i < len(found)]
        hit += holder == [k]
        print(f"  field #{k} (index {found[k][0]}) -> text landed in field "
              f"{holder[0] if holder else 'nowhere'}")
    return hit, min(3, len(found))


def test_ambiguous_identity_keeps_the_callers_coordinates():
    src = Path(find_hd()).read_text()
    assert "len(same) == 1" in src, "`hd tap` still follows a non-unique identity match"


if __name__ == "__main__":
    from suites import APPS  # noqa: E402

    test_ambiguous_identity_keeps_the_callers_coordinates()
    print("regression: an ambiguous re-match does not move the tap  OK\n")

    fixed, old = find_hd(), old_revision()
    for key in sys.argv[1:] or ["lesspass"]:
        pkg = APPS[key]["pkg"]
        print(f"{key} — this revision:")
        hit, n = lands_on_indexed_field(fixed, pkg)
        print(f"  {hit}/{n} taps landed on the indexed field")
        if old and old != fixed:
            print(f"{key} — previous revision:")
            was, n_old = lands_on_indexed_field(old, pkg)
            print(f"  {was}/{n_old} taps landed on the indexed field")
            assert hit >= was, "the fix made tap targeting worse"
        assert hit == n, "a tap did not land on the field it was given"
