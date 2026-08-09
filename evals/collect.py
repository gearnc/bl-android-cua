"""Metric extraction for the hybrid-vs-bare eval.

Perception cost is read straight off the session's last `context_growth_update` event, which the
harness emits per iteration with exact per-tool accounting:

    tool_aggregates[].approx_ant_tokens   tokens that tool's output added to the context
    total_tool_output_images              screenshots the model actually consumed
    current_context_tokens                final context size

That beats estimating from log text, and it is identical bookkeeping for both arms, so nothing
in the comparison depends on a fudge factor. Perception is split two ways:

    image tokens  -> screenshots, i.e. `computer`/browser tool output
    text  tokens  -> UI trees, i.e. `exec` output (hd see, uiautomator dump, or whatever the
                     agent rolled itself)

Pure parsing; makes no tool calls. Feed it the JSON body of that event.
"""
import json
import re

SHOT_TOKENS = 1500      # what one screenshot costs the model, for image->token conversion
PERCEPTION_TOOLS = {"exec", "get_output", "scripted_tools"}
IMAGE_TOOLS = {"computer", "browser", "screenshot"}


def parse_growth(text):
    """Extract the JSON body from a `devin_session_events action=details` dump."""
    m = re.search(r'contents:\s*(\{.*\})\s*$', text, re.S)
    if not m:
        raise ValueError("no contents JSON in event details")
    return json.loads(m.group(1))


def metrics(g):
    """Reduce one context_growth_update to the numbers the writeup needs."""
    agg = {t["tool_name"]: t for t in g["tool_aggregates"]}
    text_tokens = sum(t["approx_ant_tokens"] for n, t in agg.items() if n in PERCEPTION_TOOLS)
    images = g.get("total_tool_output_images", 0)
    image_tokens = sum(t["approx_ant_tokens"] for n, t in agg.items() if n in IMAGE_TOOLS)
    if images and not image_tokens:
        image_tokens = images * SHOT_TOKENS
    return dict(
        iterations=g.get("iteration_count", 0),
        tool_calls=sum(t["call_count"] for t in agg.values()),
        exec_calls=sum(t["call_count"] for n, t in agg.items() if n in PERCEPTION_TOOLS),
        screenshots=images,
        text_tokens=text_tokens,
        image_tokens=image_tokens,
        perception_tokens=text_tokens + image_tokens,
        context_tokens=g.get("current_context_tokens", 0),
    )


def mean_sd(xs):
    xs = list(xs)
    if not xs:
        return 0.0, 0.0
    m = sum(xs) / len(xs)
    if len(xs) < 2:
        return m, 0.0
    return m, (sum((x - m) ** 2 for x in xs) / (len(xs) - 1)) ** 0.5


def cv(xs):
    """Coefficient of variation — the run-to-run instability the eval is meant to surface."""
    m, s = mean_sd(xs)
    return s / m if m else 0.0
