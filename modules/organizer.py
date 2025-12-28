from __future__ import annotations

from datetime import datetime
from pathlib import Path


def ensure_year_month_dir(target_root: Path, dt: datetime) -> Path:
    year_dir = target_root / f"{dt.year:04d}"
    month_dir = year_dir / f"{dt.month:02d}"
    month_dir.mkdir(parents=True, exist_ok=True)
    return month_dir


def build_target_path(target_root: Path, dt: datetime, filename: str) -> Path:
    base_dir = ensure_year_month_dir(target_root, dt)
    return base_dir / filename
