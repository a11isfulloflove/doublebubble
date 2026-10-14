"""YouTube downloader helper. Runs under apps/api/.venv312 (Python 3.12).

Called by the backend as a subprocess because this stack needs a modern
Python for stable TLS impersonation. Prints a single JSON line on stdout.

Usage:
    downloader.py meta <link>
    downloader.py download <link> <output_dir>
"""
import base64
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app import browser_tls

browser_tls.apply()

from curl_cffi import requests as browser_requests
from pytubefix import YouTube
from pytubefix.exceptions import VideoUnavailable

ATTEMPTS = 10
RETRY_DELAYS = [3, 5, 8, 12, 18, 25, 30, 30, 30]


def slug_title(text):
    return "-".join(text.split())


def fetch_meta(link):
    yt = YouTube(link)
    title = yt.title
    thumb = browser_requests.get(
        yt.thumbnail_url, impersonate="chrome", timeout=15
    ).content
    return {
        "title": title,
        "slug": slug_title(title),
        "thumbnail_base64": base64.b64encode(thumb).decode("utf-8"),
    }


def fetch_download(link, output_dir):
    yt = YouTube(link)
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    path = yt.streams.get_audio_only().download(
        output_path=output_dir,
        filename=yt.title + ".m4a",
    )
    return {"path": path, "title": yt.title}


def _log(msg):
    log_path = Path(__file__).resolve().parent / "downloader.log"
    try:
        with open(log_path, "a") as f:
            f.write(f"{time.strftime('%H:%M:%S')} {msg}\n")
    except OSError:
        pass


def run_with_retries(fn, *args):
    last_error = None
    for attempt in range(1, ATTEMPTS + 1):
        try:
            result = fn(*args)
            if attempt > 1:
                _log(f"succeeded on attempt {attempt}")
            return result
        except Exception as e:
            last_error = e
            _log(f"attempt {attempt} failed: {type(e).__name__}: {str(e)[:120]}")
            print(
                f"attempt {attempt} failed: {type(e).__name__}", file=sys.stderr, flush=True
            )
            delay = RETRY_DELAYS[min(attempt - 1, len(RETRY_DELAYS) - 1)]
            time.sleep(delay)
    raise last_error


def main():
    mode = sys.argv[1]
    link = sys.argv[2]
    if mode == "meta":
        result = run_with_retries(fetch_meta, link)
    elif mode == "download":
        result = run_with_retries(fetch_download, link, sys.argv[3])
    else:
        raise SystemExit(f"unknown mode: {mode}")
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    try:
        main()
    except VideoUnavailable as e:
        print(f"VideoUnavailable: {e}", file=sys.stderr, flush=True)
        sys.exit(2)
    except Exception as e:
        print(f"{type(e).__name__}: {e}", file=sys.stderr, flush=True)
        sys.exit(1)
