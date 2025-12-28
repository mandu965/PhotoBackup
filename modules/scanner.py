from __future__ import annotations

from pathlib import Path
from typing import Iterable


def iter_files(source_dir: Path, extensions: Iterable[str]) -> Iterable[Path]:
    ext_set = {e.lower() for e in extensions}
    for path in source_dir.rglob('*'):
        if not path.is_file():
            continue
        if path.suffix.lower() in ext_set:
            yield path
