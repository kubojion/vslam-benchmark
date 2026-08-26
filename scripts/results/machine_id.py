#!/usr/bin/env python3
"""Return a stable, non-identifying ID for the host running the benchmark."""

from __future__ import annotations

import hashlib
import hmac
import os
import uuid
from pathlib import Path


NAMESPACE = b"vslam-benchmark/result-machine-id/v1"


def _fallback_path() -> Path:
    base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / "vslam-benchmark" / "machine-id"


def _machine_secret() -> bytes:
    path = Path("/etc/machine-id")
    try:
        value = path.read_text(encoding="ascii").strip()
        if len(value) == 32:
            return bytes.fromhex(value)
    except (OSError, ValueError):
        pass

    fallback = _fallback_path()
    try:
        value = fallback.read_text(encoding="ascii").strip()
        return uuid.UUID(value).bytes
    except (OSError, ValueError):
        fallback.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        value = uuid.uuid4()
        tmp = fallback.with_suffix(".tmp")
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w", encoding="ascii") as stream:
            stream.write(str(value) + "\n")
        os.replace(tmp, fallback)
        return value.bytes


def get_machine_id() -> str:
    digest = hmac.new(_machine_secret(), NAMESPACE, hashlib.sha256).hexdigest()
    return f"machine-{digest[:12]}"


if __name__ == "__main__":
    print(get_machine_id())
