from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Iterable, Optional

from modules.backup import BackupOptions, BackupResult, run_backup
from modules.logutil import setup_logging


def parse_env_file(path: Path) -> dict:
    data: dict[str, str] = {}
    if not path.exists():
        return data
    for line in path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def load_config(path: Optional[Path]) -> dict:
    data: dict[str, str] = {}
    if path is None:
        return data
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    if path.suffix.lower() == '.json':
        obj = json.loads(path.read_text(encoding='utf-8'))
        if isinstance(obj, dict):
            data = {str(k): str(v) for k, v in obj.items()}
        return data
    return parse_env_file(path)


def parse_extensions(value: Optional[str]) -> list[str]:
    if not value:
        return [".jpg", ".jpeg", ".png", ".heic", ".mp4", ".mov"]
    parts = [p.strip().lower() for p in value.split(',') if p.strip()]
    return [p if p.startswith('.') else f".{p}" for p in parts]


def resolve_setting(cli_value: Optional[str], config: dict, env_file: dict, key: str) -> Optional[str]:
    if cli_value:
        return cli_value
    if key in config:
        return config[key]
    return env_file.get(key)


def main() -> int:
    parser = argparse.ArgumentParser(description="Photo backup program (MVP)")
    parser.add_argument('--source', help='Source directory')
    parser.add_argument('--target', help='Target directory')
    parser.add_argument('--config', help='Config path (.env or config.json)')
    parser.add_argument('--dry-run', action='store_true', help='Dry run')
    parser.add_argument('--hash', action='store_true', dest='use_hash', help='Hash-based dedup')
    parser.add_argument('--copy-heic-on-fail', action='store_true', help='Copy HEIC on conversion failure')
    parser.add_argument('--workers', type=int, default=1, help='Worker count (MVP runs as 1)')
    parser.add_argument('--extensions', help='Override extensions list')
    args = parser.parse_args()

    config_path = Path(args.config) if args.config else None
    config = load_config(config_path) if config_path else {}
    env = parse_env_file(Path('.env'))

    source = resolve_setting(args.source, config, env, 'SOURCE_DIR')
    target = resolve_setting(args.target, config, env, 'TARGET_DIR')
    if not source or not target:
        parser.error('source and target are required (via args, config, or .env)')

    source_dir = Path(source).expanduser()
    target_dir = Path(target).expanduser()

    log_dir = Path('logs')
    logger = setup_logging(log_dir)

    if args.workers != 1:
        logger.warning("workers is %s but MVP runs single-threaded", args.workers)

    extensions = parse_extensions(args.extensions)

    options = BackupOptions(
        source_dir=source_dir,
        target_dir=target_dir,
        dry_run=args.dry_run,
        use_hash=args.use_hash,
        copy_heic_on_fail=args.copy_heic_on_fail,
        workers=1,
        extensions=extensions,
    )

    logger.info("Starting backup")
    logger.info("Source: %s", source_dir)
    logger.info("Target: %s", target_dir)
    logger.info("Extensions: %s", ", ".join(extensions))
    logger.info("Dry run: %s", args.dry_run)
    logger.info("Hash dedup: %s", args.use_hash)
    logger.info("Copy HEIC on fail: %s", args.copy_heic_on_fail)

    result = run_backup(options, logger)

    summary = (
        f"scanned={result.scanned}, backed_up={result.backed_up}, "
        f"converted={result.converted}, skipped_duplicate={result.skipped_duplicate}, "
        f"failed={result.failed}"
    )
    print(summary)
    logger.info("Summary: %s", summary)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
