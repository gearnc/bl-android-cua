"""The eval matrix: which cells to run, and the exact session spec for each.

Pure — no tool calls. The caller (a `scripted_tools` snippet, see README) does the launching,
because tool calls made from an imported module are rejected by the runner.

A cell is `"<app>|<arm>|<rep>"`, e.g. `markor|bare|2`.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from suites import APPS, build_prompt  # noqa: E402

# `bare` is the baseline every ratio is taken against: it is the only arm with no tool handed to
# it. `acli` measures DioxusLabs/accessibility-cli, prebuilt into the snapshot.
ARMS = ("hybrid", "bare", "acli")
BASELINE = "bare"

# The standard 6-app subset: two apps per UI toolkit, chosen because their suites are long,
# fully offline and machine-verifiable, and because they sit at opposite ends of each toolkit's
# difficulty (a file/text app and a settings-heavy one).
DEFAULT_APPS = ("markor", "amaze",          # Views
                "seal", "unitto",           # Compose
                "joplin", "lesspass")       # React Native

# Identical for every arm. Grading reads these fields instead of parsing the child's prose.
SCHEMA = {
    "type": "object",
    "properties": {
        "per_task": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "n": {"type": "integer"},
                    "status": {"type": "string", "enum": ["done", "partial", "failed"]},
                    "note": {"type": "string"},
                },
                "required": ["n", "status"],
            },
        },
        "n_done": {"type": "integer"},
        "n_partial": {"type": "integer"},
        "n_failed": {"type": "integer"},
        "final_dump": {"type": "string", "description": "verbatim output of the adb state dump"},
        "app_version": {"type": "string", "description": "version from the app's About screen"},
    },
    "required": ["per_task", "n_done", "n_partial", "n_failed", "final_dump"],
}


def cells(apps=DEFAULT_APPS, arms=ARMS, reps=2):
    return [f"{app}|{arm}|{rep}"
            for app in apps for arm in arms for rep in range(1, reps + 1)]


def spec(cell):
    """The child-session spec for one cell. Tags are what makes the runs findable later."""
    app, arm, rep = cell.split("|")
    a = APPS[app]
    return dict(prompt=build_prompt(app, arm),
                title=f"[eval] {a['label']} — {arm} — run {rep}",
                tags=["android-cua-eval", f"app:{app}", f"arm:{arm}",
                      f"stack:{a['stack']}", f"rep:{rep}"])


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="print the matrix, or one cell's prompt")
    ap.add_argument("--apps", default=",".join(DEFAULT_APPS))
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--reps", type=int, default=2)
    ap.add_argument("--prompt", help="print the full prompt for this cell and exit")
    a = ap.parse_args()
    if a.prompt:
        print(spec(a.prompt)["prompt"])
        sys.exit()
    ks = cells(tuple(x for x in a.apps.split(",") if x),
               tuple(x for x in a.arms.split(",") if x), reps=a.reps)
    print(f"{len(ks)} cells")
    for k in ks:
        print("  ", k)
