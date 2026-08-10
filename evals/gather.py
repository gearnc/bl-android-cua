"""Parsing helpers for the collection step. Pure — the caller makes the tool calls.

The runner rejects tool calls issued from an imported module, so `scripted_tools` snippets in
README.md own every `call_tool`, and everything they need to interpret a response lives here.
"""
import json
import re

SID = re.compile(r"session_id[=:]\s*([0-9a-f]{32})")
CURSOR = re.compile(r"Pass after=(\S+) to fetch")
TRUNCATED = re.compile(r"<truncation_notice>")
# `first=100` overflows the tool-output cap on a busy session: the page is cut off mid-list, the
# "More results" cursor survives at the top, so pagination continues and the tail of every page
# is lost without an error. That silently truncated the 2026-08-10 run's growth series at a
# different iteration in every cell (28% of one run's turns, 100% of another's) — an arm whose
# context grows slowly loses the most, which is the arm the comparison is against.
PAGE = 40
EVENT_ID = re.compile(r"\[(event-[0-9a-f]+)\]")
# The `(shell: <id>)` suffix is only present when the command fits on one line; a multi-line
# command is listed with its first line and nothing else, so requiring the suffix drops every
# heredoc and python -c block — which is exactly where a state-writing `adb shell` hides.
EXEC_CMD = re.compile(r"exec:\s(.+?)(?:\s\(shell:\s*\w+\))?\s*$", re.M)


def session_ids(create_output):
    """Session ids from a devin_session_create response, in the order the specs were sent."""
    return SID.findall(create_output)


def next_cursor(list_output):
    m = CURSOR.search(list_output)
    return m.group(1) if m else None


def truncated(list_output):
    """Whether the tool cut this page off — the ids after the cut are gone, not paginated."""
    return bool(TRUNCATED.search(list_output))


def event_ids(list_output):
    if truncated(list_output):
        raise ValueError("page truncated — refetch this cursor with a smaller `first`")
    return EVENT_ID.findall(list_output)


def exec_commands(list_output):
    if truncated(list_output):
        raise ValueError("page truncated — refetch this cursor with a smaller `first`")
    return EXEC_CMD.findall(list_output)


def status(get_output):
    """State + ACU + whether the child has delivered its structured output yet."""
    def g(pat, cast=str, default=None):
        m = re.search(pat, get_output)
        return cast(m.group(1)) if m else default
    return dict(state=g(r"\bstatus:\s*(\w+)", default="?"),
                detail=g(r"status_detail:\s*(\w+)", default="?"),
                acu=g(r"acus_consumed:\s*([\d.]+)", float, 0.0),
                has_output="structured_output:" in get_output)


def task_counts(get_output):
    def g(pat):
        m = re.search(pat, get_output)
        return int(m.group(1)) if m else None
    return dict(n_done=g(r"n_done:\s*(\d+)"),
                n_partial=g(r"n_partial:\s*(\d+)"),
                n_failed=g(r"n_failed:\s*(\d+)"))


def growth(details_output):
    """The JSON body of a context_growth_update event."""
    m = re.search(r"contents:\s*(\{.*\})\s*$", details_output, re.S)
    if not m:
        raise ValueError("no contents JSON in event details")
    return json.loads(m.group(1))
