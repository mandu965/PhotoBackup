from __future__ import annotations

from pathlib import Path

from PIL import Image
from pillow_heif import register_heif_opener


register_heif_opener()


def convert_heic_to_jpg(source: Path, target: Path, quality: int = 95) -> None:
    with Image.open(source) as img:
        rgb = img.convert('RGB')
        rgb.save(target, format='JPEG', quality=quality)
