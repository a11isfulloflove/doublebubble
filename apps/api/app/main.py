import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Form, HTTPException

from .db import collection
from .services.youtube import get_video_meta
from .worker import queue_loop

queue_task: asyncio.Task | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global queue_task
    queue_task = asyncio.create_task(queue_loop())
    yield
    queue_task.cancel()


app = FastAPI(lifespan=lifespan)


@app.post("/transcribe")
async def transcribe(link: str = Form(...)):
    print(f"link: {link}")

    existing = await collection.find_one({"link": link})

    if existing:
        if existing.get("status") == "queued":
            return {"status": "queued", "message": "This video is already in the queue"}
        if existing.get("status") == "processing":
            return {"status": "processing", "message": "This video is already being processed"}
        if existing.get("status") == "done":
            return {"status": "done", "message": "This video already exists. Please!! check the feed"}

    doc = {"link": link, "status": "queued", **get_video_meta(link)}

    await collection.insert_one(doc)
    return {"status": "queued"}


@app.get("/getallvideos")
async def get_subs():
    cursor = collection.find(
        {},
        {"_id": 0, "link": 1, "title": 1, "slug": 1, "thumbnail_base64": 1, "status": 1},
    )
    vids = await cursor.to_list(length=None)
    return vids


@app.post("/getbyslugtitle")
async def get_video(slugtitle: str = Form(...)):
    print(f"slug title: {slugtitle}")

    existing = await collection.find_one({"slug": slugtitle}, {"_id": 0})
    return existing


@app.delete("/deletevideo/{slug}")
async def delete_video(slug: str):
    print(f"Удаление видео со слагом: {slug}")
    result = await collection.delete_one({"slug": slug})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Видео не найдено")

    return {"status": "success", "message": f"Видео со слагом '{slug}' удалено"}
