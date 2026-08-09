"""Where a run's raw data lives. Override with EVAL_DATA to keep several runs side by side."""
import os
from pathlib import Path

DATA = Path(os.environ.get("EVAL_DATA", Path(__file__).resolve().parent / "data"))
DATA.mkdir(parents=True, exist_ok=True)

RUNS = DATA / "runs.json"          # cell -> session id
METRICS = DATA / "metrics.json"    # cell -> ACU + perception accounting
TASKS = DATA / "tasks.json"        # cell -> n_done / n_partial / n_failed
BYPASS = DATA / "bypass.json"      # cell -> shortcut-command counts
REPORT = DATA / "report.md"
