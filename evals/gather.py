"""Parsing helpers for the collection step. Pure — the caller makes the tool calls.

The runner rejects tool calls issued from an imported module, so `scripted_tools` snippets in
README.md own every `call_tool`, and everything they need to interpret a response lives here.
"""
import json
import re

SID = re.compile(r"session_id[=:]\s*([0-9a-f]{32})")
CURSOR = re.compile(r"Pass after=(\S+) to fetch")
EVENT_ID = re.compile(r"\[(event-[0-9a-f]+)\]")
EXEC_CMD = re.compile(r"exec:\s(.+?)\s\(shell:")


def session_ids(create_output):
    """Session ids from a devin_session_create response, in the order the specs were sent."""
    return SID.findall(create_output)


def next_cursor(list_output):
    m = CURSOR.search(list_output)
    return m.group(1) if m else None


def event_ids(list_output):
    return EVENT_ID.findall(list_output)


def exec_commands(list_output):
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
