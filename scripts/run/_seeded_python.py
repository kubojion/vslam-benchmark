#!/usr/bin/env python3
"""Run a Python script after applying a deterministic process-wide RNG seed."""

from __future__ import annotations

import random
import runpy
import sys


def main() -> int:
    if len(sys.argv) < 3:
        print(f"usage: {sys.argv[0]} SEED SCRIPT [ARG ...]", file=sys.stderr)
        return 2
    seed = int(sys.argv[1])
    script = sys.argv[2]
    sys.argv = sys.argv[2:]
    random.seed(seed)
    try:
        import numpy as np
        np.random.seed(seed)
    except ImportError:
        pass
    try:
        import torch
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except ImportError:
        pass
    runpy.run_path(script, run_name="__main__")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
