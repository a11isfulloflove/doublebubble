# doublesub API

FastAPI backend: downloads YouTube audio, transcribes it with Whisper, translates segments with MarianMT, stores results in MongoDB.

## Layout

```
app/
├── main.py        # FastAPI app + routes + queue startup
├── config.py      # settings from .env
├── db.py          # Mongo client + collection
├── worker.py      # queue loop + processing pipeline
├── browser_tls.py # routes pytubefix through Chrome-impersonated TLS
└── services/
    ├── youtube.py       # calls downloader.py as a subprocess
    ├── transcription.py # Whisper
    └── translation.py   # MarianMT (ko → en)
downloader.py     # YouTube meta + audio download (runs under .venv312!)
```

## Two Pythons, on purpose

The backend (Whisper, MarianMT, FastAPI) runs on your usual Python via
`requirements.txt`. YouTube downloads need a modern Python for stable TLS
impersonation, so they run in a separate small venv as a subprocess:

```bash
cd apps/api
python3 -m venv .venv312        # needs Python 3.12: brew install python@3.12
.venv312/bin/pip install pytubefix curl_cffi
```

## Setup

```bash
cd apps/api
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
cp .env.example .env
```

Requires a running MongoDB on `MONGO_URL` (default `mongodb://localhost:27017/`).

## Run

```bash
python3 -m uvicorn app.main:app --reload
```

The worker queue starts automatically with the server and processes one video at a time (`queued` → `processing` → `done`).

## Configuration

All settings live in `.env` (see `.env.example`): Mongo connection, download dir, Whisper model/language, translation model, queue poll interval.
