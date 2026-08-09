"""Billed input tokens per run, from the `context_growth_update` series.

Perception tokens answer "what did one look cost". They do not answer "what did the run cost":
ACU is mostly inference, and inference bills the whole resident context on every turn, so a
token added at turn i is charged again at every turn after i. Billed input is therefore the
integral of context size over turns, not the sum of tool outputs.

The 2026-08-09 run is the cautionary tale — hybrid spent 0.50x the perception tokens of bare and
still billed the same (median 3.23 vs 3.18 Mtok), because its trees stay resident while bare's
screenshots do not, leaving hybrid carrying ~11k more context across ~93 turns.

Pure functions; makes no tool calls. Feed `series` the (iteration_count, current_context_tokens)
pairs from every `context_growth_update` event of a session.
"""


def billed_tokens(series):
    """Trapezoid integral of context size over turns = tokens the run re-read to get to the end.

    Sub-sampling the series is fine (the curve is smooth and monotone between compactions), but
    it must include the first and last event or the tail is silently dropped.
    """
    pts = sorted(set(series))
    return sum((b[0] - a[0]) * (b[1] + a[1]) / 2 for a, b in zip(pts, pts[1:]))


def resident_share(billed, turns, tool_tokens):
    """How much of a run's billing is carried context rather than the tokens it just fetched.

    ~1.0 means the run is paying for what it reads; >>1 means it is paying to keep it.
    """
    return (billed / turns / tool_tokens) if turns and tool_tokens else 0.0
