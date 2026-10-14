# 🫧double더블🫧버블bubble🫧

Dual-subtitle tool for Korean YouTube videos: downloads audio, transcribes it with Whisper (Korean), translates each segment to English with MarianMT, and plays the video with both subtitle tracks side by side.

## Monorepo layout

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
python3 -m uvicorn app.main:app --reload
```

Requires a running MongoDB (default `mongodb://localhost:27017/`). See `apps/api/README.md` for details.

## Scripts

| Command         | Description                     |
| --------------- | ------------------------------- |
| `npm run dev`   | Start the web dev server        |
| `npm run build` | Type-check and build the web app |
| `npm run lint`  | Lint the web app                |

## Troubleshooting

**Video doesn't render (blank player area):** Vite's dependency cache (`apps/web/node_modules/.vite`) can go stale after dependency changes. Run `npm run dev:fresh` to clear it and restart, then hard-refresh the browser (Cmd+Shift+R).
