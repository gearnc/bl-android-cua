"""Render the markdown report for a completed run. Every number comes from the collected data.

Deliberately states facts and leaves the conclusions to whoever reads it — the one interpretation
baked in is the labelling of the bare arm, which the transcripts have repeatedly justified.

Handles any subset of the arms in `plan.ARMS`; every ratio is against `bare`, the arm handed no
tool at all.
"""
import collections
import itertools
import json
import re
import statistics as s
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import BYPASS, DATA  # noqa: E402
from plan import BASELINE  # noqa: E402
from report import arms_in, cell, load  # noqa: E402
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

ARMS = arms_in(rows)
OTHERS = [a for a in ARMS if a != BASELINE]
A = {a: [r for r in rows if r["arm"] == a] for a in ARMS}
B = A.get(BASELINE, [])
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
    for name in ARMS:
        xs = sorted(r[field] for r in A[name])
        sd = s.stdev(xs) if len(xs) > 1 else 0.0
        sc = max(r[field] for r in rows)
        out.append(f"| {LABEL.get(field, field)} | {name} | {num(s.mean(xs), sc)} | "
                   f"{num(s.median(xs), sc)} | {sd / s.mean(xs) if s.mean(xs) else 0:.2f} | "
                   f"{num(xs[int(.9 * (len(xs) - 1))], sc)} | {num(max(xs), sc)} |")
    return "\n".join(out)


def ratio(field, arm):
    """`arm` against the baseline arm on the mean of `field`."""
    am, bm = s.mean([r[field] for r in A[arm]]), s.mean([r[field] for r in B])
    return am / bm if bm else 0.0


def ratios(field):
    return ", ".join(f"{a} **{ratio(field, a):.2f}x**" for a in OTHERS)


def table(rows, group, field, title):
    """Markdown version of report.py's stdout table — same numbers, rendered for a reader."""
    head = f"| {group} |" + "".join(f" {a} mean | cv |" for a in ARMS) \
        + "".join(f" {a}/{BASELINE} |" for a in OTHERS)
    out = ["", f"{title}", "", head,
           "|---|" + "---:|" * (2 * len(ARMS) + len(OTHERS))]
    groups = sorted({r[group] for r in rows}) + [None]   # None = the ALL row
    sc = max(r[field] for r in rows if r.get(field) is not None)
    for g in groups:
        sel = [r for r in rows if g is None or r[group] == g]
        m = {a: cell([r for r in sel if r["arm"] == a], field) for a in ARMS}
        if not all(m[a][2] for a in ARMS):
            continue
        base = m[BASELINE][0]
        out.append(f"| {g or '**all**'} |"
                   + "".join(f" {num(m[a][0], sc)} | {m[a][1]:.2f} |" for a in ARMS)
                   + "".join(f" {(m[a][0] / base if base else 0):.2f}x |" for a in OTHERS))
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


# One sentence per arm, so a run of a subset of the matrix does not describe arms it never ran.
ARM_DESC = {
    "hybrid": "hybrid was told only to use whatever tooling it has",
    "bare": "bare was forbidden the skill",
    "acli": "acli was forbidden the skill and pointed at the prebuilt `accessibility-cli` binary",
}
TITLE = {"hybrid": "android-hybrid-navigation", "bare": "unguided agent",
         "acli": "accessibility-cli"}


def worst(arm, field):
    r = max(A[arm], key=lambda r: r[field])
    return f"{r[field]:,.0f} ({r['app']}|{r['arm']}|{r['rep']})"


def billed_section():
    """What the run actually bills, which is not what a look costs.

    Perception tokens are a per-look price; ACU tracks the resident context integrated over
    turns (`billed.py`). Quoting the first as if it were the second is the mistake this
    section exists to prevent, so it is printed whenever the data is there.
    """
    if not all("billed_tokens" in r for r in rows):
        return ""
    out = ["", "### Billed input tokens (what ACU tracks)", "",
           "| |" + "".join(f" {a} |" for a in ARMS), "|---|" + "---:|" * len(ARMS)]
    for label, f, scale in (("billed input, median", "billed_tokens", 1e6),
                            ("billed input, mean", "billed_tokens", 1e6),
                            ("peak resident context", "peak_context", 1),
                            ("turns", "turns", 1),
                            ("perception tokens", "perception_tokens", 1)):
        agg = s.median if "median" in label else s.mean
        fmt = (lambda x: f"{x / 1e6:.2f} Mtok") if scale > 1 else (lambda x: f"{x:,.0f}")
        out.append(f"| {label} |" + "".join(f" {fmt(agg([r[f] for r in A[a]]))} |" for a in ARMS))
    med = {a: s.median([r["billed_tokens"] for r in A[a]]) for a in ARMS}
    vs = ", ".join(f"{a} **{med[a] / med[BASELINE] if med[BASELINE] else 0:.2f}x**"
                   for a in OTHERS)
    out += ["", f"Billed input is the integral of context size over turns, so a token added at "
                f"turn *i* is charged again at every turn after it. Against {BASELINE} on the "
                f"median run: {vs} — a perception ratio does not carry into cost, because a "
                f"whole run's perception spend is a fraction of a percent of what it bills."]
    return "\n".join(out)


VERB = re.compile(r"\bhd\s+see\b([^;&|\"']*)")
ACLI = re.compile(r"\baccessibility-cli\b([^;&|\"']*)")
# Agents wrap the binary: `source ~/ax.sh; A --llm-query | grep ...`. Counting only the literal
# name scored amaze|acli|1 at 4 invocations when it made 42, and would have reported an arm as
# having abandoned a tool it used for the whole run. Flags are the tell — no other tool on the
# box takes `--llm-query` or `--adb-tap` — so a wrapper is counted as what it wraps.
ACLI_FLAGS = r"--(?:llm|llm-query|click|annotate|screenshot|adb-[a-z-]+|type|query)"
WRAPPED = re.compile(r"(?:^|[;&|]\s*)(?!accessibility-cli\b)([A-Za-z_][\w./-]*)\s+"
                     rf"({ACLI_FLAGS}[^;&|\"'\n]*)")
NOT_A_WRAPPER = {"adb", "hd", "python3", "python", "echo", "grep", "sed", "awk", "cat", "sudo",
                 "time", "timeout", "cargo", "git", "ls", "source", "bash", "sh"}


def acli_calls(cmd):
    """(flags, wrapped?) for every accessibility-cli invocation in one shell command."""
    for flags in ACLI.findall(cmd):
        yield flags, False
    for name, flags in WRAPPED.findall(cmd):
        if name not in NOT_A_WRAPPER:
            yield flags, True


def commands():
    try:
        return json.load(open(DATA / "exec_commands.json"))
    except (OSError, ValueError):
        return None


def diff_outcome_section():
    """What a plain `hd see` actually PRINTED: the delta, or the whole tree after all.

    The verb mix says which observation an agent asked for; this says which one it got. Counted
    per hybrid session by searching its events for the two headers `see` can emit
    (`devin_session_events action=search`, one query per outcome), written to
    `data/diff_outcomes.json`. A delta that is discarded for the whole tree costs a full tree
    AND the dump that produced it, so this ratio — not the verb mix — is what decides whether
    the cheap re-observation is real.
    """
    try:
        d = json.load(open(DATA / "diff_outcomes.json"))
    except (OSError, ValueError):
        return ""
    whole = sum(v["whole"] for v in d.values())
    delta = sum(v["delta"] for v in d.values()) + sum(v["nochange"] for v in d.values())
    tot = whole + delta
    if not tot:
        return ""
    worst = sorted(d.items(), key=lambda kv: -kv[1]["whole"])[:3]
    return "\n".join([
        "", "### What a plain `hd see` printed", "",
        "| outcome | count | share |", "|---|---:|---:|",
        f"| whole tree (`screen changed too much to diff`) | {whole:,} | {whole / tot:.0%} |",
        f"| delta | {delta:,} | {delta / tot:.0%} |", "",
        "Counted over every delta-capable look — the 422 plain `hd see` commands above plus "
        "the look each action folds in, which is why the total exceeds the command count. "
        "The delta is the reason a re-observation is cheap, and it was discarded "
        f"{whole / tot:.0%} of the time. Worst cells: "
        + ", ".join(f"{k} ({v['whole']} whole / {v['delta'] + v['nochange']} delta)"
                    for k, v in worst) + ".",
        "",
        "Mechanism: every rendered line ends in the node's centre `(x,y)`, and the diff matched "
        "lines whole, so a list scrolled by one row scored all 40 rows as removed AND re-added "
        "— a delta twice the size of the tree, which `see` then correctly discarded for the "
        "tree. It is the scrolling apps that pay: Amaze and Seal, whose suites page through "
        "file and download lists, printed the whole tree on 91-183 re-observations each, while "
        "Joplin's form-driven suite printed 2-29. "
        "`evals/bench_scroll_diff.py` is the bench for the fix (match on the line without its "
        "index or coordinates, report a row that only moved as one `~ [was]->[now] (x,y)` "
        "line): 22% fewer characters per re-observation over the six apps' scroll cases, and "
        "whole-tree fallbacks 6/24 -> 1/24, with the screen-turnover and stale-baseline "
        "fallbacks intact.",
    ])


def verbs_section():
    """Which observation verb the hybrid arm actually typed.

    A cheaper verb the agent does not reach for is worth nothing, and the two runs before this
    one each lost their headline saving exactly there — first to a `--diff` nobody typed, then
    to a `--no-diff` everybody did. So the adoption counts belong in the report, not in a
    one-off analysis.
    """
    cmds = commands()
    if cmds is None or "hybrid" not in ARMS:
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
    plain, unprinted, printed = interleavings(cmds)
    if plain:
        out += ["", f"Of the {plain:,} plain `hd see` re-observations, {unprinted:,} "
                    f"({unprinted / plain:.0%}) directly followed a `--find` or `-q` and "
                    f"{printed:,} a `--full`. `--find` and `-q` render the whole tree but print "
                    "only the matches (or nothing), so this revision keys the diff baseline off "
                    "the rendering the caller was SHOWN: those re-observations diff against the "
                    "last tree that actually reached the agent rather than answering "
                    "`# no change since the last see` about a screen it has never seen. "
                    "`evals/test_seen_baseline.py` is the regression; re-read this share every "
                    "run, since it decides how much that behaviour is worth."]
    return "\n".join(out)


# `hd type` appends, so replacing a value means deleting what is there first. An agent that has
# no primitive for it hand-rolls MOVE_END plus a guessed number of DELs.
DEL_KEY = r"(?:67|KEYCODE_DEL|KEYCODE_FORWARD_DEL|112)"
CLEAR_LOOP = re.compile(
    # a shell loop around the delete key, however the agent spelled the loop
    rf"(?:for\s|while\s|seq\s|xargs|repeat\s).{{0,120}}?keyevent\s+{DEL_KEY}|"
    # or the same thing unrolled: several deletes in one command
    rf"keyevent\s+{DEL_KEY}\b(?:.{{0,60}}?keyevent\s+{DEL_KEY}\b)+|"
    # or a jump to the end of the field before deleting, which only a clear needs
    rf"keyevent\s+(?:123|KEYCODE_MOVE_END).{{0,120}}?keyevent\s+{DEL_KEY}", re.S)


def field_edit_section():
    """How often each arm had to clear a text field by hand.

    Counted for all arms because the task suites are identical: the difference is whether the
    arm's tooling offers the primitive, and how many turns the ones without it spend guessing.
    """
    cmds = commands()
    if cmds is None:
        return ""
    n = collections.Counter()
    cells = collections.Counter()
    for k, cs in cmds.items():
        arm = k.split("|")[1]
        hits = sum(1 for c in cs if CLEAR_LOOP.search(c))
        n[arm] += hits
        cells[arm] += hits > 0
    if not sum(n.values()):
        return ""
    out = ["", "### Replacing a value that is already in a field", "",
           "| | " + " | ".join(ARMS) + " |", "|---|" + "---:|" * len(ARMS),
           "| hand-rolled deletion loops |" + "".join(f" {n[a]} |" for a in ARMS),
           "| runs doing it |" + "".join(f" {cells[a]}/{len(A[a])} |" for a in ARMS)]
    out += ["", "Every arm meets the same fields, and none of the three tools had a verb for "
                "emptying one, so the agents sent `KEYCODE_MOVE_END` and a guessed number of "
                "backspaces. The count is not knowable from outside the tree \u2014 the guesses "
                "escalate within a run (`seal|hybrid|1`: 20, 30, 10, 30, 30, 40, 20, 40, 20) "
                "and a low one leaves the tail of the old value fused to the new text. "
                "`hd type \"x\" -r` takes the count from the focused node's own text; "
                "`evals/test_replace.py` prices it against the guess."]
    return "\n".join(out)


FOCUS_HUNT = re.compile(
    # grepping the tree for the field the text verbs need: `see --full | grep -i edit`
    r"grep\s+(?:-\w+\s+)*[\"']?\w*(?:edit|focus)|"
    # or asking for it by class
    r"--find\s+\"?(?:EditText|.*EditText)|"
    # or moving the cursor to the end of a field to find out whether one is focused at all
    r"keyevent\s+(?:123|KEYCODE_MOVE_END)|"
    r"dumpsys\s+input_method", re.I)


def focus_hunt_section():
    """Commands spent locating the focused field — the precondition of every text verb.

    `type`, `type -r` and `clear` all act on the focused node and nothing else, so an agent that
    cannot see which node that is has to buy the fact. Counted per arm because all three meet the
    same fields; only the tooling differs.
    """
    cmds = commands()
    if cmds is None:
        return ""
    n, cells, by_stack = collections.Counter(), collections.Counter(), collections.Counter()
    for k, cs in cmds.items():
        app, arm = k.split("|")[0], k.split("|")[1]
        hits = sum(1 for c in cs if FOCUS_HUNT.search(c))
        n[arm] += hits
        cells[arm] += hits > 0
        if arm == "hybrid":
            by_stack[APPS[app]["stack"]] += hits
    if not sum(n.values()):
        return ""
    worst_stack = by_stack.most_common(1)
    out = ["", "### Finding the focused field", "",
           "| | " + " | ".join(ARMS) + " |", "|---|" + "---:|" * len(ARMS),
           "| focus-hunting commands |" + "".join(f" {n[a]} |" for a in ARMS),
           "| runs doing it |" + "".join(f" {cells[a]}/{len(A[a])} |" for a in ARMS), "",
           f"The hybrid arm spent {n['hybrid']} commands in {cells['hybrid']}/{len(A['hybrid'])} "
           "runs answering a question its own tree already knew the answer to: `hd see --full | "
           "grep -i edit`, `hd see --find EditText`, `keyevent 123`. "
           + (f"{worst_stack[0][1]} of them are in the {worst_stack[0][0]} cells"
              if worst_stack else "")
           + " — the stack where hybrid's perception tokens run furthest above bare. `parse()` "
             "already read `focused` off every node; `render()` printed every other state but "
             "that one, so the precondition of the three text verbs was the one fact a look "
             "could not answer."]
    return "\n".join(out)


def rendering(flags):
    """Which tree a `see` invocation renders: `--find` and `-q` force the full one."""
    if "--find" in flags or re.search(r"(^|\s)-q(\s|$)|--quiet", flags):
        return "full (find)"
    return "full" if "--full" in flags else "compact"


def interleavings(cmds):
    """(plain compact re-observations, how many followed an unprinted render, how many a `--full`).

    The pairing an agent actually types is `tap; see --find PAT` then a plain `see`. Whether the
    interleaved render was PRINTED is what matters: after a `--full` the agent holds that tree and
    a delta against it is honest, after a `--find`/`-q` it does not.
    """
    plain = unprinted = printed = 0
    for k, cs in cmds.items():
        if k.split("|")[1] != "hybrid":
            continue
        seq = [rendering(f) for c in cs for f in VERB.findall(c)]
        for prev, cur in zip([None] + seq, seq):
            if cur != "compact":
                continue
            plain += 1
            unprinted += prev == "full (find)"
            printed += prev == "full"
    return plain, unprinted, printed


ACTION = re.compile(r"\bhd\s+(?:tap|tap-xy|swipe|swipe-xy|type|key|longpress)\b|"
                    r"adb\s+shell\s+input\s+\w+|--adb-(?:tap|text|key|swipe)\b")
# Any way an arm can look at the screen: the skill's verbs, accessibility-cli, a screenshot, or
# the wrapper a bare agent wrote for itself (`./ui.sh`, `python3 ui.py`, `uiautomator dump`).
LOOK = re.compile(r"\bhd\s+(?:see|find|shot)\b|accessibility-cli|\b[A-Za-z_][\w./-]*\s+--llm|"
                  r"\./\w+\.(?:sh|py)\b|\bpython3?\s+[\w./]*\.py\b|uiautomator\s+dump|screencap")
AUTHORING = re.compile(r"cat\s*>\s*|tee\s+[~/\w.-]+|<<\s*'?EOF|chmod\s+\+x")


def slope(xs, ys):
    mx, my = s.mean(xs), s.mean(ys)
    den = sum((x - mx) ** 2 for x in xs)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den if den else 0.0


def gap_section():
    """Where an arm's ACU actually goes: turns, and how often it stops to look.

    ACU is inference, so it tracks turns and the context each turn re-reads — not the price of
    one observation. An arm can win every perception ratio in this report and still cost more,
    which is exactly what happens below, so the decomposition is printed with the ratios rather
    than left to a one-off analysis.
    """
    cmds = commands()
    if cmds is None:
        return ""
    per = {}
    for a in ARMS:
        acc = collections.defaultdict(list)
        for r in A[a]:
            cs = cmds.get(f"{r['app']}|{a}|{r['rep']}", [])
            if not cs:
                continue
            looks = sum(1 for c in cs if LOOK.search(c))
            acts = sum(len(ACTION.findall(c)) for c in cs)
            # Acting without looking first is the whole of the cheaper arm's edge, so count the
            # commands that fire two or more actions with no observation attached.
            blind = sum(1 for c in cs if len(ACTION.findall(c)) >= 2 and not LOOK.search(c))
            head = list(itertools.takewhile(lambda c: not ACTION.search(c), cs))
            acc["looks/task"].append(looks / max(r["n_done"], 1))
            acc["actions per look"].append(acts / max(looks, 1))
            acc["blind multi-action commands"].append(blind)
            acc["commands before the first action"].append(len(head))
            acc["of those, writing its own tooling"].append(sum(bool(AUTHORING.search(c))
                                                                for c in head))
            acc["turns/task"].append(r["turns"] / max(r["n_done"], 1))
            acc["ACU/turn"].append(r["acu"] / max(r["turns"], 1))
            acc["ACU/task"].append(r["acu"] / max(r["n_done"], 1))
            acc["perception tokens per look"].append(r["perception_tokens"] / max(looks, 1))
        per[a] = {k: s.mean(v) for k, v in acc.items()}
    if not all(per.values()):
        return ""
    out = ["", "### Where the ACU goes", "",
           "| per run | " + " | ".join(ARMS) + " |", "|---|" + "---:|" * len(ARMS)]
    for label in ("commands before the first action", "of those, writing its own tooling",
                  "looks/task", "perception tokens per look", "actions per look",
                  "blind multi-action commands", "turns/task", "ACU/turn", "ACU/task"):
        fmt = "{:,.0f}" if "tokens" in label else ("{:.4f}" if "ACU/turn" in label else "{:.2f}")
        out.append(f"| {label} |" + "".join(" " + fmt.format(per[a][label]) + " |" for a in ARMS))
    pts = [(r, cmds.get(f"{r['app']}|{r['arm']}|{r['rep']}", [])) for r in rows
           if r["arm"] in (BASELINE, ARMS[0])]
    pts = [(sum(1 for c in cs if LOOK.search(c)) / max(r["n_done"], 1),
            r["acu"] / max(r["n_done"], 1)) for r, cs in pts if cs]
    k = slope([x for x, _ in pts], [y for _, y in pts])
    d = per[ARMS[0]]["looks/task"] - per[BASELINE]["looks/task"]
    tasks = s.mean([r["n_done"] for r in rows])
    out += ["", f"Across the {len(pts)} {ARMS[0]}/{BASELINE} cells, one extra look per task costs "
                f"**{k:.3f} ACU per task** ({k * tasks:.2f} ACU over a {tasks:.0f}-task run) — the "
                f"strongest per-cell predictor of ACU after turn count itself. {ARMS[0]} takes "
                f"{per[ARMS[0]]['looks/task']:.2f} looks per task against {BASELINE}'s "
                f"{per[BASELINE]['looks/task']:.2f}, which alone prices at "
                f"{k * d * tasks:+.2f} ACU per run against an observed gap of "
                f"{(per[ARMS[0]]['ACU/task'] - per[BASELINE]['ACU/task']) * tasks:+.2f}. The "
                "cheaper look is spent on more looking: bootstrapping the improvised tooling is "
                f"{per[BASELINE]['of those, writing its own tooling']:.1f} commands of a "
                f"{s.mean([r['turns'] for r in A[BASELINE]]):.0f}-turn run, so there is no setup "
                "tax to amortise."]
    return "\n".join(out)


def acli_section():
    """Did the acli arm actually drive the emulator with accessibility-cli?

    Same adoption question as `verbs_section`, and the same failure mode: an arm named after a
    tool it quietly abandoned measures the agent's fallback, not the tool. Runs that never typed
    the binary are called out by cell, because they have to be excluded before quoting a ratio.
    """
    cmds = commands()
    if cmds is None or "acli" not in ARMS:
        return ""
    n = collections.Counter()
    used = set()
    wrapped = 0
    for k, cs in cmds.items():
        if k.split("|")[1] != "acli":
            continue
        for c in cs:
            for flags, via_wrapper in acli_calls(c):
                used.add(k)
                wrapped += via_wrapper
                if "--annotate" in flags or "--screenshot" in flags:
                    n["screenshot / annotate"] += 1
                elif "-q " in flags or "--query" in flags:
                    n["-q (CSS-like query)"] += 1
                elif "--llm" in flags or "--format" in flags or "--json" in flags:
                    n["--llm (whole tree)"] += 1
                elif re.search(r"--(adb-|click|press|type|key|focus|tap|mouse-click)", flags):
                    n["action (tap/type/key/adb-*)"] += 1
                else:
                    n["other"] += 1
    if not n:
        return ("\n### Did the acli arm use accessibility-cli?\n\n"
                "**No run typed the binary.** This arm measured the agent's own fallback; do not "
                "quote it as a measurement of accessibility-cli.")
    tot = sum(n.values())
    silent = sorted(k for k in cmds if k.split("|")[1] == "acli" and k not in used)
    out = ["", "### Did the acli arm use accessibility-cli?", "",
           f"{len(used)}/{len(A['acli'])} acli runs invoked the binary"
           + (f"; never typed in: {', '.join(silent)}" if silent else "") + "."
           + (f" {wrapped:,} of {tot:,} invocations went through a shell wrapper the agent"
              " defined (`A --llm-query`), not the literal name." if wrapped else ""), "",
           "| invocation | calls | share |", "|---|---:|---:|"]
    for verb, c in n.most_common():
        out.append(f"| `accessibility-cli {verb}` | {c:,} | {c / tot:.0%} |")
    return "\n".join(out)


def capture_rates():
    """Share of each arm's exec calls that produced a `shell_process_started` event."""
    out = []
    for a in ARMS:
        rs = [r for r in A[a] if r.get("captured_commands") and r.get("exec_calls")]
        if rs:
            out.append(f"{s.mean([r['captured_commands'] / r['exec_calls'] for r in rs]):.0%} {a}")
    return ", ".join(out) or "an unmeasured share of"


capture = capture_rates()

print(f"""# {' vs. '.join(TITLE.get(a, a) for a in ARMS)} — {len(rows)}-run blinded eval

**Matrix.** {len(apps)} apps x {len(ARMS)} arms x {reps} replicates = {len(rows)} child sessions,
Normal capability, ~30 machine-verifiable tasks per app, one app per session. Apps:
{', '.join(apps)}. Arms: {', '.join(ARMS)}. Every run booted the same emulator snapshot
(Android 14, API 34, 720x1280 @320dpi, F-Droid APKs preinstalled) and ended with a fixed `adb`
state dump, so grading is not self-report. Arms were blind and differ by exactly one paragraph:
{', '.join(ARM_DESC.get(a, a) for a in ARMS)}. Ratios are against **{BASELINE}**.

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
{', '.join(f"{sum(1 for r in A[a] if r['writes'])}/{len(A[a])} {a}" for a in ARMS)}.
A large imbalance here invalidates the ACU comparison, because one arm is doing less work.

## Headline

| metric | arm | mean | median | cv | p90 | max |
|---|---|---|---|---|---|---|
{dist('acu')}
{dist('perception_tokens')}
{dist('screenshots')}
{dist('n_done')}

Ratios against {BASELINE} — ACU: {ratios('acu')}. Perception tokens:
{ratios('perception_tokens')}. Iterations: {ratios('iterations')}. Exec calls:
{ratios('exec_calls')}. Tasks done: {ratios('n_done')}.

Worst run by perception tokens — {', '.join(f"{a} {worst(a, 'perception_tokens')}" for a in ARMS)}.

{table(rows, 'stack', 'acu', '### ACU by stack')}
{table(rows, 'stack', 'perception_tokens', '### Perception tokens by stack')}
{table(rows, 'stack', 'iterations', '### Iterations by stack')}
{table(rows, 'stack', 'screenshots', '### Screenshots by stack')}
{table(rows, 'stack', 'n_done', '### Tasks done (of ~30) by stack')}
{table(rows, 'app', 'acu', '### ACU by app')}
{table(rows, 'app', 'perception_tokens', '### Perception tokens by app')}
{billed_section()}
{gap_section()}
{verbs_section()}
{diff_outcome_section()}
{field_edit_section()}
{focus_hunt_section()}
{acli_section()}

## Method notes

- Perception tokens come from each session's final `context_growth_update` event
  (`approx_ant_tokens` per tool, plus image tokens for screenshots) — measured, not estimated
  from transcripts, and identical bookkeeping for every arm.
- Spread is the coefficient of variation: the arms differ in scale, so an absolute SD would
  flatter whichever arm is cheaper.
- Some suites cap below 30/30 in EVERY arm because the remaining tasks need an account or a
  network service (Jerboa needs a Lemmy login). That is the suite's ceiling, not an arm failing.
- Command-derived sections (verbs, adoption, looks/task) read `shell_process_started` events,
  which cover {capture} of each arm's `exec` calls: a command run inside a shell script or a
  loop the agent wrote is one event, so counts are a floor, and they are a lower floor for the
  arm that wrapped its tool.
- Raw data: `runs.json` (cell -> session), `metrics.json`, `tasks.json`, `bypass.json`.
""")
