"""Reading `devin_session_events action=details` without letting it censor the numbers.

Pure helpers only: tool calls made from an imported module are rejected by the runner, so the
`call_tool` loop stays in the inline snippet and imports these. Produces the rows that go into
metrics.json / billed.json; see `evals/README.md` for the two independent truncations these
work around.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from collect import metrics  # noqa: E402
from gather import PAGE, event_ids, next_cursor, truncated  # noqa: E402

ITER = re.compile(r"[\"']?iteration[\"']?\s*[:=]\s*(\d+)")
EVENT_HEAD = re.compile(r"(?=^--- event-[0-9a-f]+ ---$)", re.M)


def sample(ids, n=12):
    """Evenly spaced event ids, always including the first and last (billed.py needs both)."""
    if len(ids) <= n:
        return list(ids)
    step = (len(ids) - 1) / (n - 1)
    picks = sorted({int(round(i * step)) for i in range(n)} | {0, len(ids) - 1})
    return [ids[i] for i in picks]


# A `details` response overflows the tool's output cap at ~5k chars, and the overflow is cut
# mid-JSON — the same failure mode as a truncated list page, one call over. Ask for few enough
# events that every page closes its braces.
DETAIL_BATCH = 1
OVERFLOW = re.compile(r"Full output written to:\s*(\S+)")
# `details` clips a content field at ~2k chars unless max_content_length is passed explicitly —
# and it clips it in place, with no truncation notice and no overflow file. The tail of a
# context_growth_update is where `current_context_tokens` lives, so an unset cap silently
# censors the growth series of exactly the busiest (largest tool_aggregates) cells.
MAX_CONTENT = 100000


def chunks(xs, n=DETAIL_BATCH):
    return [xs[i:i + n] for i in range(0, len(xs), n)]


def whole(details_output):
    """The full response, reading the overflow file when the tool cut the output.

    A cut `details` response loses the tail of the JSON — `current_context_tokens` lives there —
    so a silently truncated page would censor the growth series exactly like a truncated list
    page did in the 2026-08-10 run.
    """
    if not truncated(details_output):
        return details_output
    m = OVERFLOW.search(details_output)
    if not m:
        raise ValueError("details truncated with no overflow file")
    return Path(m.group(1)).read_text(errors="replace")


def split_details(details_output):
    """A `details` response covering several events -> one text block per event."""
    parts = EVENT_HEAD.split(details_output)
    return [p for p in parts if p.lstrip().startswith("--- event-")]


def contents(part):
    """The `contents:` JSON of one event block, brace-matched.

    `gather.growth` anchors on the end of the string, so it only reads the *last* event of a
    response and nothing at all once responses are concatenated. Matching braces instead means
    every event in a page parses, and a body cut short raises rather than being skipped.
    """
    i = part.find("contents: {")
    if i < 0:
        raise ValueError("no contents JSON in event details")
    i = part.index("{", i)
    depth = 0
    for j in range(i, len(part)):
        depth += (part[j] == "{") - (part[j] == "}")
        if depth == 0:
            return json.loads(part[i:j + 1])
    raise ValueError("contents JSON truncated mid-body")


def series_from(details_outputs):
    """(iteration_count, current_context_tokens) pairs from one or more details responses."""
    if isinstance(details_outputs, str):
        details_outputs = [details_outputs]
    out = []
    for text in details_outputs:
        for part in split_details(text):
            g = contents(part)
            out.append((g.get("iteration_count", 0), g.get("current_context_tokens", 0)))
    return sorted(set(out))


def last_iteration(list_output):
    """Highest iteration number mentioned in an iteration_stats listing (the cross-check)."""
    ns = [int(x) for x in ITER.findall(list_output)]
    return max(ns) if ns else None


def row(get_out, growth_out, series, acu):
    m = metrics(contents(split_details(growth_out)[-1]))
    m["acu"] = acu
    m["peak_context"] = max([c for _, c in series] + [m["context_tokens"]])
    m["turns"] = m["iterations"]
    return m


__all__ = ["PAGE", "MAX_CONTENT", "event_ids", "next_cursor", "truncated", "chunks", "whole",
           "sample", "contents", "series_from", "last_iteration", "row", "split_details"]
