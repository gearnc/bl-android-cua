"""Turn metrics.json + tasks.json into the hybrid-vs-bare comparison tables.

Reports mean and spread for ACU and perception tokens, per stack and overall. Spread is given
as the coefficient of variation, because the arms differ in scale and an absolute SD would make
the cheaper arm look artificially stable.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from collect import mean_sd  # noqa: E402
from paths import METRICS, TASKS  # noqa: E402


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
    """One field, hybrid vs bare, grouped by `group` (a row key such as 'app' or 'stack')."""
    lines = [f"\n{title}",
             f"{group:<18} {'hybrid mean':>12} {'cv':>6} {'bare mean':>12} {'cv':>6} {'ratio':>7}"]
    groups = sorted({r[group] for r in rows})
    for g in groups:
        h = [r for r in rows if r[group] == g and r["arm"] == "hybrid"]
        b = [r for r in rows if r[group] == g and r["arm"] == "bare"]
        if not h or not b:
            continue
        hm, hcv, hn = cell(h, field)
        bm, bcv, bn = cell(b, field)
        ratio = hm / bm if bm else 0
        lines.append(f"{g:<18} {hm:>12.0f} {hcv:>6.2f} {bm:>12.0f} {bcv:>6.2f} {ratio:>7.2f}")
    h = [r for r in rows if r["arm"] == "hybrid"]
    b = [r for r in rows if r["arm"] == "bare"]
    hm, hcv, _ = cell(h, field)
    bm, bcv, _ = cell(b, field)
    lines.append(f"{'ALL':<18} {hm:>12.0f} {hcv:>6.2f} {bm:>12.0f} {bcv:>6.2f} "
                 f"{hm / bm if bm else 0:>7.2f}")
    return "\n".join(lines)


if __name__ == "__main__":
    from suites import APPS
    rows = load()
    for r in rows:
        r["stack"] = APPS[r["app"]]["stack"]
    print(f"{len(rows)} runs: "
          f"{sum(1 for r in rows if r['arm'] == 'hybrid')} hybrid / "
          f"{sum(1 for r in rows if r['arm'] == 'bare')} bare")
    for field, title in [("acu", "ACU"),
                         ("perception_tokens", "PERCEPTION TOKENS"),
                         ("screenshots", "SCREENSHOTS"),
                         ("iterations", "ITERATIONS"),
                         ("context_tokens", "FINAL CONTEXT TOKENS"),
                         ("n_done", "TASKS DONE (of 30)")]:
        print(table(rows, "stack", field, f"=== {title} by stack ==="))
    print(table(rows, "app", "acu", "=== ACU by app ==="))
    print(table(rows, "app", "perception_tokens", "=== perception tokens by app ==="))
