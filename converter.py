import os
import shutil
import subprocess
from pathlib import Path

from PIL import Image


def _ffmpeg_bin() -> str:
    path = shutil.which("ffmpeg") or shutil.which(
        "ffmpeg", path="/opt/homebrew/bin:/usr/local/bin:/usr/bin"
    )
    if not path:
        raise EnvironmentError(
            "ffmpeg 가 설치되지 않았습니다. 'brew install ffmpeg' 로 설치해주세요."
        )
    return path


def convert_to_webp(src: str, dst_dir: str, quality: int = 80) -> str:
    src_path = Path(src)
    dst_path = Path(dst_dir) / (src_path.stem + ".webp")

    with Image.open(src_path) as img:
        img.save(dst_path, "WEBP", quality=quality)

    return str(dst_path)


def convert_to_webm(src: str, dst_dir: str, crf: int = 33) -> str:
    src_path = Path(src)
    dst_path = Path(dst_dir) / (src_path.stem + ".webm")

    cmd = [
        _ffmpeg_bin(), "-y",
        "-i", str(src_path),
        "-c:v", "libvpx-vp9",
        "-crf", str(crf),
        "-b:v", "0",
        "-c:a", "libopus",
        str(dst_path),
    ]

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg 오류:\n{result.stderr[-1000:]}")

    return str(dst_path)


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"}
VIDEO_EXTS = {".mp4", ".mov", ".avi", ".mkv", ".flv", ".wmv"}


def batch_convert(
    src_dir: str,
    dst_dir: str,
    delete_original: bool = False,
    quality: int = 80,
    crf: int = 33,
    on_progress=None,  # callback(current, total, filename)
) -> dict:
    src_path = Path(src_dir)
    files = [
        f for f in src_path.iterdir()
        if f.is_file() and f.suffix.lower() in IMAGE_EXTS | VIDEO_EXTS
    ]

    results = {"success": 0, "fail": 0, "errors": []}
    total = len(files)

    for i, f in enumerate(files):
        if on_progress:
            on_progress(i + 1, total, f.name)
        try:
            ext = f.suffix.lower()
            if ext in IMAGE_EXTS:
                convert_to_webp(str(f), dst_dir, quality=quality)
            else:
                convert_to_webm(str(f), dst_dir, crf=crf)

            if delete_original:
                f.unlink()
            results["success"] += 1
        except Exception as e:
            results["fail"] += 1
            results["errors"].append(f"{f.name}: {e}")

    return results


