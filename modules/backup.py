from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import shutil
from typing import Iterable

from modules.converter import convert_heic_to_jpg
from modules.dedup import is_duplicate
from modules.metadata import get_capture_datetime
from modules.organizer import build_target_path
from modules.scanner import iter_files


@dataclass
class BackupOptions:
    source_dir: Path
    target_dir: Path
    dry_run: bool
    use_hash: bool
    copy_heic_on_fail: bool
    workers: int
    extensions: list[str]


@dataclass
class BackupResult:
    scanned: int = 0
    backed_up: int = 0
    converted: int = 0
    skipped_duplicate: int = 0
    failed: int = 0


def _get_datetime_fallback(path: Path) -> datetime:
    stat = path.stat()
    return datetime.fromtimestamp(stat.st_mtime)


def run_backup(options: BackupOptions, logger) -> BackupResult:
    result = BackupResult()
    if not options.source_dir.exists():
        raise FileNotFoundError(f"Source not found: {options.source_dir}")
    options.target_dir.mkdir(parents=True, exist_ok=True)

    # TODO(확장): 파일 단위 병렬 처리(멀티스레딩/멀티프로세싱) 적용
    for src in iter_files(options.source_dir, options.extensions):
        result.scanned += 1
        try:
            capture_dt = get_capture_datetime(src) or _get_datetime_fallback(src)
            dest_name = src.name
            is_heic = src.suffix.lower() == '.heic'
            if is_heic:
                dest_name = src.with_suffix('.jpg').name
            dest = build_target_path(options.target_dir, capture_dt, dest_name)

            if is_duplicate(src if not is_heic else src, dest, options.use_hash):
                result.skipped_duplicate += 1
                logger.info("SKIP_DUPLICATE %s -> %s", src, dest)
                continue

            if options.dry_run:
                logger.info("DRY_RUN %s -> %s", src, dest)
                continue

            if is_heic:
                try:
                    convert_heic_to_jpg(src, dest)
                    result.converted += 1
                    result.backed_up += 1
                    logger.info("CONVERTED %s -> %s", src, dest)
                except Exception as exc:
                    result.failed += 1
                    logger.error("HEIC_CONVERT_FAIL %s (%s)", src, exc)
                    if options.copy_heic_on_fail:
                        fallback_dest = dest.with_suffix('.heic')
                        if not is_duplicate(src, fallback_dest, options.use_hash):
                            shutil.copy2(src, fallback_dest)
                            result.backed_up += 1
                            logger.info("COPIED_HEIC_FAILOVER %s -> %s", src, fallback_dest)
                    continue
            else:
                shutil.copy2(src, dest)
                result.backed_up += 1
                logger.info("COPIED %s -> %s", src, dest)

        except Exception as exc:
            result.failed += 1
            logger.error("FAILED %s (%s)", src, exc)
            continue

    return result
