"""Render the markdown report for a completed run. Every number comes from the collected data.

Deliberately states facts and leaves the conclusions to whoever reads it — the one interpretation
baked in is the labelling of the bare arm, which the transcripts have repeatedly justified.
"""
import collections
import json
import re
import statistics as s
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import BYPASS, DATA  # noqa: E402
from report import cell, load  # noqa: E402
from suites import APPS  # noqa: E402

rows = load()
for r in rows:
    r["stack"] = APPS[r["app"]]["stack"]
try:
    byp = json.load(open(BYPASS))
except (OSError, ValueError):
    byp = {}
for r in rows:
    b = byp.get(f"{r['app']}|{r['arm']}|{r['rep']}", {})
    r["writes"] = b.get("writes", 0)

H = [r for r in rows if r["arm"] == "hybrid"]
B = [r for r in rows if r["arm"] == "bare"]
apps = sorted({r["app"] for r in rows})
reps = max(r["rep"] for r in rows)


LABEL = {"acu": "ACU", "perception_tokens": "perception tokens",
         "screenshots": "screenshots", "n_done": "tasks done (of ~30)"}


def num(x, scale):
    """One decimal for small-valued fields (ACU, task counts), where units hide the difference.

    Chosen per table from the field's largest value, so a column is formatted consistently.
    """
    return f"{x:,.1f}" if scale < 100 else f"{x:,.0f}"


def dist(field):
    out = []
    for name, arm in (("hybrid", H), ("bare", B)):
        xs = sorted(r[field] for r in arm)
        sd = s.stdev(xs) if len(xs) > 1 else 0.0
        sc = max(r[field] for r in rows)
        out.append(f"| {LABEL.get(field, field)} | {name} | {num(s.mean(xs), sc)} | "
                   f"{num(s.median(xs), sc)} | {sd / s.mean(xs) if s.mean(xs) else 0:.2f} | "
                   f"{num(xs[int(.9 * (len(xs) - 1))], sc)} | {num(max(xs), sc)} |")
    return "\n".join(out)


def ratio(field):
    hm, bm = s.mean([r[field] for r in H]), s.mean([r[field] for r in B])
    return hm / bm if bm else 0.0


def table(rows, group, field, title):
    """Markdown version of report.py's stdout table — same numbers, rendered for a reader."""
    out = ["", f"{title}", "",
           f"| {group} | hybrid mean | cv | bare mean | cv | hybrid/bare |",
           "|---|---:|---:|---:|---:|---:|"]
    groups = sorted({r[group] for r in rows}) + [None]   # None = the ALL row
    sc = max(r[field] for r in rows if r.get(field) is not None)
    for g in groups:
        sel = [r for r in rows if g is None or r[group] == g]
        h = [r for r in sel if r["arm"] == "hybrid"]
        b = [r for r in sel if r["arm"] == "bare"]
        if not h or not b:
            continue
        hm, hcv, _ = cell(h, field)
        bm, bcv, _ = cell(b, field)
        out.append(f"| {g or '**all**'} | {num(hm, sc)} | {hcv:.2f} | {num(bm, sc)} | {bcv:.2f} | "
                   f"{hm / bm if bm else 0:.2f}x |")
    return "\n".join(out)


TREE_MAX = 5    # screenshots: at or below this the run was reading trees, not pixels
CUA_MIN = 20    # at or above this it really was doing visual CUA
n_tree = sum(1 for r in B if r["screenshots"] <= TREE_MAX)
n_cua = sum(1 for r in B if r["screenshots"] >= CUA_MIN)

# Which experiment this run turned out to be. The 2026-08 baseline and the 2026-08-09 run were
# mostly improvised tree tooling; a later run of the identical matrix was mostly pixels. Stating
# it from the data is the difference between a valid comparison and a mislabelled one.
if n_cua > n_tree:
    VERDICT = "Mostly it IS screenshot-driven CUA."
    FRAMING = ("So this mostly measures **the skill vs. visual computer use**, the comparison "
               "the plugin README claims — and it is the flattering framing, not the harsh one.")
elif n_tree > n_cua:
    VERDICT = "Mostly it is not screenshot-driven CUA."
    FRAMING = ("So this mostly measures **the skill vs. agent-improvised tree tooling**, not "
               "the skill vs. looking at the screen — a harsher bar than the README's.")
else:
    VERDICT = "It is an even split between pixels and improvised tree tooling."
    FRAMING = ("So the arm is a mixture, and the perception ratio is an average over two "
               "different experiments; read the per-run screenshot counts before quoting it.")


def worst(arm, field):
    r = max(arm, key=lambda r: r[field])
    return f"{r[field]:,.0f} ({r['app']}|{r['arm']}|{r['rep']})"


def billed_section():
    """What the run actually bills, which is not what a look costs.

    Perception tokens are a per-look price; ACU tracks the resident context integrated over
    turns (`billed.py`). Quoting the first as if it were the second is the mistake this
    section exists to prevent, so it is printed whenever the data is there.
    """
    if not all("billed_tokens" in r for r in rows):
        return ""
    def med(arm, f):
        return s.median([r[f] for r in arm])
    out = ["", "### Billed input tokens (what ACU tracks)", "",
           "| | hybrid | bare |", "|---|---:|---:|"]
    for label, f, scale in (("billed input, median", "billed_tokens", 1e6),
                            ("billed input, mean", "billed_tokens", 1e6),
                            ("peak resident context", "peak_context", 1),
                            ("turns", "turns", 1),
                            ("perception tokens", "perception_tokens", 1)):
        agg = s.median if "median" in label else s.mean
        h, b = agg([r[f] for r in H]), agg([r[f] for r in B])
        fmt = (lambda x: f"{x / 1e6:.2f} Mtok") if scale > 1 else (lambda x: f"{x:,.0f}")
        out.append(f"| {label} | {fmt(h)} | {fmt(b)} |")
    hb, bb = med(H, "billed_tokens"), med(B, "billed_tokens")
    share = 100 * s.mean([r["perception_tokens"] for r in H]) / hb
    out += ["", f"Billed input is the integral of context size over turns, so a token added at "
                f"turn *i* is charged again at every turn after it. Hybrid/bare on the median "
                f"run: **{hb / bb:.2f}x** — a perception ratio of "
                f"{ratio('perception_tokens'):.2f}x does not carry into cost, because a whole "
                f"run's perception spend is ~{share:.2f}% "
                f"of what it bills."]
    return "\n".join(out)


VERB = re.compile(r"\bhd\s+see\b([^;&|\"']*)")


def verbs_section():
    """Which observation verb the hybrid arm actually typed.

    A cheaper verb the agent does not reach for is worth nothing, and the two runs before this
    one each lost their headline saving exactly there — first to a `--diff` nobody typed, then
    to a `--no-diff` everybody did. So the adoption counts belong in the report, not in a
    one-off analysis.
    """
    try:
        cmds = json.load(open(DATA / "exec_commands.json"))
    except (OSError, ValueError):
        return ""
    n = collections.Counter()
    for k, cs in cmds.items():
        if k.split("|")[1] != "hybrid":
            continue
        for c in cs:
            for flags in VERB.findall(c):
                if "--find" in flags:
                    n["see --find"] += 1
                elif "--no-diff" in flags:
                    n["see --no-diff (opt out of the delta)"] += 1
                elif "--full" in flags:
                    n["see --full"] += 1
                elif re.search(r"(^|\s)-q(\s|$)|--quiet", flags):
                    n["see -q (capture, print nothing)"] += 1
                else:
                    n["see (delta on a re-observation)"] += 1
    if not n:
        return ""
    tot = sum(n.values())
    out = ["", "### Which observation verb the hybrid arm typed", "",
           "| verb | calls | share |", "|---|---:|---:|"]
    for verb, c in n.most_common():
        out.append(f"| `hd {verb}` | {c:,} | {c / tot:.0%} |")
    return "\n".join(out)


print(f"""# android-hybrid-navigation vs. unguided agent — {len(rows)}-run blinded eval

**Matrix.** {len(apps)} apps x 2 arms x {reps} replicates = {len(rows)} child sessions, Normal
capability, ~30 machine-verifiable tasks per app, one app per session. Apps:
{', '.join(apps)}. Every run booted the same emulator snapshot (Android 14, API 34, 720x1280
@320dpi, F-Droid APKs preinstalled) and ended with a fixed `adb` state dump, so grading is not
self-report. Arms were blind: hybrid sessions were told only to use whatever tooling they have;
bare sessions were forbidden from reading or invoking the skill.

## What the bare arm actually does

**{VERDICT}** Denied the skill, agents sometimes reinvent it — a bare session may write a
`uiautomator dump` wrapper (`ui.sh`, `t.sh`, `ui.py`) in its first minute and grep it — and
sometimes just looks at the screen. Counting a run as *improvised tree tooling* at
<= {TREE_MAX} screenshots and as *visual CUA* at >= {CUA_MIN}: {n_tree}/{len(B)} bare runs
improvised tree tooling, {n_cua}/{len(B)} did visual CUA,
{len(B) - n_tree - n_cua} sat in between. Median bare run:
{s.median([r['screenshots'] for r in B]):.0f} screenshots across ~30 tasks. {FRAMING} Re-check
this split every run before quoting the numbers; it decides which experiment you ran, and it
has flipped between runs of the same matrix.

The opposite failure — completing tasks by writing device state instead of driving the UI
(`adb shell mkdir` for "create a folder") — is counted too: runs touching device state directly,
{sum(1 for r in H if r['writes'])}/{len(H)} hybrid vs {sum(1 for r in B if r['writes'])}/{len(B)}
bare. A large imbalance here invalidates the ACU comparison, because one arm is doing less work.

## Headline

| metric | arm | mean | median | cv | p90 | max |
|---|---|---|---|---|---|---|
{dist('acu')}
{dist('perception_tokens')}
{dist('screenshots')}
{dist('n_done')}

Hybrid/bare ratios: ACU **{ratio('acu'):.2f}x**, perception tokens
**{ratio('perception_tokens'):.2f}x**, iterations **{ratio('iterations'):.2f}x**, exec calls
**{ratio('exec_calls'):.2f}x**, tasks done **{ratio('n_done'):.2f}x**.

Worst run by perception tokens — hybrid {worst(H, 'perception_tokens')},
bare {worst(B, 'perception_tokens')}.

{table(rows, 'stack', 'acu', '### ACU by stack')}
{table(rows, 'stack', 'perception_tokens', '### Perception tokens by stack')}
{table(rows, 'stack', 'iterations', '### Iterations by stack')}
{table(rows, 'stack', 'screenshots', '### Screenshots by stack')}
{table(rows, 'stack', 'n_done', '### Tasks done (of ~30) by stack')}
{table(rows, 'app', 'acu', '### ACU by app')}
{table(rows, 'app', 'perception_tokens', '### Perception tokens by app')}
{billed_section()}
{verbs_section()}

## Method notes

- Perception tokens come from each session's final `context_growth_update` event
  (`approx_ant_tokens` per tool, plus image tokens for screenshots) — measured, not estimated
  from transcripts, and identical bookkeeping for both arms.
- Spread is the coefficient of variation: the arms differ in scale, so an absolute SD would
  flatter whichever arm is cheaper.
- Some suites cap below 30/30 in BOTH arms because the remaining tasks need an account or a
  network service (Jerboa needs a Lemmy login). That is the suite's ceiling, not an arm failing.
- Raw data: `runs.json` (cell -> session), `metrics.json`, `tasks.json`, `bypass.json`.
""")
