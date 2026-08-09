"""Regression: every checkable node must show its state in the rendered tree.

`seal|hybrid|1` in the 2026-08-09 run spent 33 screenshots (49.5k of its 79.2k perception
tokens) reading Compose toggles, because `render` only printed `checked=` for nodes whose class
was Switch/CheckBox/RadioButton/ToggleButton — and Compose renders every switch as a bare
`android.view.View` with `checkable="true"`. So the one profile with no labels to fall back on
was also the one profile where state was invisible, and the only way left to read it was pixels.

Asserts on a captured Compose settings screen (no navigation needed, so it runs anywhere) and
then against live trees: no node may be checkable without its state being rendered.
"""

import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from env import ENV, find_hd  # noqa: E402
from test_diff import launch  # noqa: E402

HD_PY = find_hd()
sys.path.insert(0, str(Path(HD_PY).parent))
from hd import detect_profile, dump_xml, parse, render  # noqa: E402

# Screens reached by a plain launch that are known to carry toggles.
SCREENS = {"seal": ["Settings", "General"],
           "unitto": ["Settings", "Formatting"],
           "markor": [],
           "amaze": [],
           "joplin": [],
           "lesspass": []}


# A real Seal settings row, as `uiautomator dump` emits it: a Compose switch is a bare View.
COMPOSE_XML = """<?xml version='1.0' encoding='UTF-8'?>
<hierarchy rotation="0">
 <node class="android.widget.FrameLayout" bounds="[0,0][720,1280]">
  <node class="androidx.compose.ui.platform.ComposeView" bounds="[0,0][720,1280]">
   <node class="android.view.View" text="" content-desc="" checkable="true" checked="true"
         clickable="true" enabled="true" bounds="[0,592][720,787]"/>
   <node class="android.widget.TextView" text="Download notification" bounds="[40,620][580,680]"/>
   <node class="android.view.View" text="" content-desc="" checkable="true" checked="false"
         clickable="true" enabled="true" bounds="[0,1030][720,1185]"/>
   <node class="android.widget.TextView" text="Save thumbnail" bounds="[40,1060][580,1120]"/>
  </node>
 </node>
</hierarchy>"""


def test_compose_switch_state_is_rendered():
    nodes, _ = parse(COMPOSE_XML)
    _, lines = render(nodes, False, "compose")
    out = "\n".join(lines)
    assert "checked=true" in out and "checked=false" in out, (
        "Compose switch state missing from the tree — the agent can only get it from a "
        f"screenshot:\n{out}")
    print("compose switch state rendered from attributes, not class: ok")
    return out


def tree_for_current_screen():
    nodes, _ = parse(dump_xml())
    profile, _ = detect_profile(nodes)
    _, lines = render(nodes, False, profile)
    return nodes, lines, profile


def hd(*args):
    return subprocess.run(["python3", HD_PY, *args], capture_output=True, text=True,
                          env=ENV).stdout


def check(app, pkg, path):
    launch(pkg)
    for step in path:
        out = hd("see", "--find", step)
        m = re.search(r"^\s*\[(\d+)\].*<C", out, re.M)
        if not m:
            break
        hd("tap", m.group(1))
    nodes, lines, profile = tree_for_current_screen()
    rendered = "\n".join(lines)
    checkable = [n for n in nodes if n["checkable"] and n["checked"] in ("true", "false")]
    shown = rendered.count("checked=")
    print(f"{app:<10} profile={profile:<8} checkable_nodes={len(checkable):<3} "
          f"rendered checked= {shown}")
    assert shown >= len(checkable), (
        f"{app}: {len(checkable)} checkable nodes but only {shown} render their state — "
        "the agent has to screenshot to read them")
    return len(checkable), shown


if __name__ == "__main__":
    from suites import APPS  # noqa: E402

    test_compose_switch_state_is_rendered()
    which = sys.argv[1:] or list(SCREENS)
    for app in which:
        try:
            check(app, APPS[app]["pkg"], SCREENS.get(app, []))
        except Exception as e:                                   # noqa: BLE001
            print(f"{app}: FAILED {e}")
            raise
