from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

from PIL import Image
from PIL.ExifTags import TAGS


EXIF_DATE_TAGS = {"DateTimeOriginal", "DateTime", "DateTimeDigitized"}


def _parse_exif_datetime(value: str) -> Optional[datetime]:
    try:
        return datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
    except ValueError:
        return None


def get_capture_datetime(path: Path) -> Optional[datetime]:
    ext = path.suffix.lower()
    if ext in {".jpg", ".jpeg", ".png", ".heic"}:
        try:
            with Image.open(path) as img:
                exif = img.getexif()
                if not exif:
                    return None
                for tag_id, value in exif.items():
                    tag = TAGS.get(tag_id, str(tag_id))
                    if tag in EXIF_DATE_TAGS and isinstance(value, str):
                        dt = _parse_exif_datetime(value)
                        if dt:
                            return dt
        except Exception:
            return None
    # TODO(확장): 영상(MP4/MOV) 촬영일 메타데이터 추출 개선(MediaInfo/ffprobe 등)
    return None
