import base64

import requests
from pytubefix import YouTube
from pytubefix.cli import on_progress
from pytubefix.exceptions import VideoUnavailable


def slug_title(text: str) -> str:
    return "-".join(text.split())


def get_video_meta(link: str) -> dict:
    try:
        yt = YouTube(link, on_progress_callback=on_progress)
    except VideoUnavailable:
        raise

    thumbnail_base64 = base64.b64encode(requests.get(yt.thumbnail_url).content).decode("utf-8")

    return {
        "title": yt.title,
        "slug": slug_title(yt.title),
        "thumbnail_base64": thumbnail_base64,
    }


def download_audio(link: str, output_dir: str) -> str:
    yt = YouTube(link)
    return yt.streams.get_audio_only().download(
        output_path=output_dir,
        filename=yt.title + ".m4a",
    )
