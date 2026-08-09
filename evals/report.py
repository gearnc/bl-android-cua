"""Turn metrics.json + tasks.json into the per-arm comparison tables.

Reports mean and spread for ACU and perception tokens, per stack and overall, for however many
arms the data contains (hybrid / bare / acli). Spread is given as the coefficient of variation,
because the arms differ in scale and an absolute SD would make the cheaper arm look artificially
stable. Ratios are taken against `bare`, the arm handed no tool.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from collect import mean_sd  # noqa: E402
from paths import METRICS, TASKS  # noqa: E402
from plan import ARMS, BASELINE  # noqa: E402


def load():
    m = json.load(open(METRICS))
    try:
        t = json.load(open(TASKS))
    except (OSError, ValueError):
        t = {}
    rows = []
    for k, v in m.items():
        if "error" in v:
            continue
        app, arm, rep = k.split("|")
        r = dict(app=app, arm=arm, rep=int(rep), **v)
        r.update(t.get(k, {}))
        rows.append(r)
    return rows


def arms_in(rows):
    """Arms actually present, in the canonical order, so a partial run still renders."""
    seen = {r["arm"] for r in rows}
    return [a for a in ARMS if a in seen] + sorted(seen - set(ARMS))


def by(rows, *keys):
    out = {}
    for r in rows:
        out.setdefault(tuple(r[k] for k in keys), []).append(r)
    return out


def cell(rows, field):
    xs = [r[field] for r in rows if r.get(field) is not None]
    m, s = mean_sd(xs)
    return m, (s / m if m else 0.0), len(xs)


def table(rows, group, field, title):
    """One field per arm, grouped by `group` (a row key such as 'app' or 'stack')."""
    arms = arms_in(rows)
    others = [a for a in arms if a != BASELINE]
    head = f"{group:<18}" + "".join(f"{a + ' mean':>13}{'cv':>6}" for a in arms) \
        + "".join(f"{a + '/' + BASELINE:>13}" for a in others)
    lines = [f"\n{title}", head]

    def row(label, sel):
        m = {a: cell([r for r in sel if r["arm"] == a], field) for a in arms}
        if not all(m[a][2] for a in arms):
            return None
        base = m[BASELINE][0] if BASELINE in m else 0
        return f"{label:<18}" + "".join(f"{m[a][0]:>13.0f}{m[a][1]:>6.2f}" for a in arms) \
            + "".join(f"{(m[a][0] / base if base else 0):>13.2f}" for a in others)

    for g in sorted({r[group] for r in rows}):
        line = row(g, [r for r in rows if r[group] == g])
        if line:
            lines.append(line)
    line = row("ALL", rows)
    if line:
        lines.append(line)
    return "\n".join(lines)


if __name__ == "__main__":
    from suites import APPS
    rows = load()
    for r in rows:
        r["stack"] = APPS[r["app"]]["stack"]
    print(f"{len(rows)} runs: " + " / ".join(
        f"{sum(1 for r in rows if r['arm'] == a)} {a}" for a in arms_in(rows)))
    for field, title in [("acu", "ACU"),
                         ("perception_tokens", "PERCEPTION TOKENS"),
                         ("screenshots", "SCREENSHOTS"),
                         ("iterations", "ITERATIONS"),
                         ("context_tokens", "FINAL CONTEXT TOKENS"),
                         ("n_done", "TASKS DONE (of 30)")]:
        print(table(rows, "stack", field, f"=== {title} by stack ==="))
    print(table(rows, "app", "acu", "=== ACU by app ==="))
    print(table(rows, "app", "perception_tokens", "=== perception tokens by app ==="))
