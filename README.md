# 🫧double더블🫧버블bubble🫧

Doublesub turns Korean YouTube videos into bilingual learning
resources. The audio is transcribed with OpenAI's Whisper, each
segment is translated to English with MarianMT, and the video plays
with both languages displayed in sync — no plugins, no manual
subtitle hunting.

It is built around a simple principle from language learning:
comprehensible input works best when meaning is available in context.
Rather than pausing to look up unfamiliar words, you keep watching
while the translation fills in exactly the parts you don't know yet.

- Synchronized **Korean subtitles** displayed over the video
- **English translation** directly beneath each line
- **Clickable full transcript** for jumping straight to any moment

## Project structure

```
doublesub/
├── apps/
│   ├── web/          # React 19 + Vite + TypeScript frontend
│   └── api/          # FastAPI backend (Whisper + MarianMT + MongoDB)
├── packages/
│   └── shared/       # @doublesub/shared — shared TS types + API client
├── package.json      # npm workspaces root
└── .gitignore
```

## Prerequisites

- [Node.js](https://nodejs.org) (v20+)
- Python 3.9+ for the backend, and [Python 3.12](https://www.python.org/downloads/) for the YouTube downloader (on mac: `brew install python@3.12`)
- A running MongoDB — quickest way: `docker run -d -p 27017:27017 mongo`

## Setup

### Web

```bash
npm install
npm run dev
```

The dev server proxies `/whisper/*` requests to the API (see `apps/web/vite.config.ts`).

### API

```bash
cd apps/api
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
cp .env.example .env
```

The backend also needs a second, tiny environment used for YouTube
downloads (modern Python for TLS impersonation):

```bash
python3.12 -m venv .venv312
.venv312/bin/pip install pytubefix curl_cffi
```

### Run

Start the API first, then the web app:

```bash
# terminal 1 — from apps/api, with .venv activated:
python3 -m uvicorn app.main:app --reload

# terminal 2 — from the repo root:
npm run dev
```

Then open http://localhost:5173. See `apps/api/README.md` for more details.

## Scripts

| Command         | Description                      |
| --------------- | -------------------------------- |
| `npm run dev`   | Start the web dev server         |
| `npm run build` | Type-check and build the web app |
| `npm run lint`  | Lint the web app                 |

## Troubleshooting

**Video doesn't render (blank player area):** Vite's dependency cache
(`apps/web/node_modules/.vite`) can go stale after dependency changes.
Run `npm run dev:fresh` to clear it and restart, then hard-refresh the
browser (Cmd+Shift+R).

**New video stuck on "VIDEO IS LOADING...":** the network that YouTube
sees can throttle downloads for minutes at a time. The backend keeps
retrying with growing pauses (~10 minutes total) — check
`apps/api/downloader.log` to watch it push through.
