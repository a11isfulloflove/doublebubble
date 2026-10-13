import os
from pathlib import Path


def _load_dotenv(path: str = ".env") -> None:
    env_path = Path(__file__).resolve().parent.parent / path
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


_load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "dubsub")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "subs")

DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "./downloads")

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "medium")
WHISPER_LANGUAGE = os.getenv("WHISPER_LANGUAGE", "ko")

TRANSLATION_MODEL = os.getenv("TRANSLATION_MODEL", "Helsinki-NLP/opus-mt-ko-en")

QUEUE_POLL_INTERVAL = float(os.getenv("QUEUE_POLL_INTERVAL", "5"))
