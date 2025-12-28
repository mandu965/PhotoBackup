from __future__ import annotations

import hashlib
from pathlib import Path


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def is_duplicate(source: Path, target: Path, use_hash: bool) -> bool:
    if not target.exists():
        return False
    try:
        if source.stat().st_size != target.stat().st_size:
            return False
        if use_hash:
            return _sha256(source) == _sha256(target)
        return True
    except OSError:
        return False
