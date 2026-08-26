#!/usr/bin/env python3
"""Write source-side ROS transport counters atomically."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional


def write_transport_stats(path: Optional[Path], **values: int) -> None:
    if path is None:
        return
    payload = {"schema": 1, **values}
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    os.replace(temporary, path)
