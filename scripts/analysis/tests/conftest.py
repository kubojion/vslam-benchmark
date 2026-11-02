"""Paths for the search's tests. Optuna lives in this worktree's private .venv (timing-search/setup_private.sh)."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / 'scripts/analysis'), str(ROOT / 'scripts/run'), str(ROOT / 'scripts/eval')]
VENV = ROOT / '.venv/lib/python3.10/site-packages'
if VENV.is_dir():
    sys.path.append(str(VENV))
