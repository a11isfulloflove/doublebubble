import json
import os
import subprocess
from pathlib import Path

from pytubefix.exceptions import VideoUnavailable

from ..config import DOWNLOADER_PYTHON

_DOWNLOADER = str(Path(__file__).resolve().parents[2] / "downloader.py")


def _run_downloader(*args, timeout):
    proc = subprocess.run(
        [DOWNLOADER_PYTHON, _DOWNLOADER, *args],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if proc.returncode == 2:
        raise VideoUnavailable(video_id=args[1])
    if proc.returncode != 0:
        detail = (proc.stderr or "").strip().splitlines()
        raise RuntimeError(detail[-1] if detail else f"downloader exited {proc.returncode}")

    lines = [line for line in proc.stdout.strip().splitlines() if line.strip()]
    return json.loads(lines[-1])


def slug_title(text: str) -> str:
    return "-".join(text.split())


def get_video_meta(link: str) -> dict:
    return _run_downloader("meta", link, timeout=600)


def download_audio(link: str, output_dir: str) -> str:
    return _run_downloader("download", link, output_dir, timeout=900)["path"]
