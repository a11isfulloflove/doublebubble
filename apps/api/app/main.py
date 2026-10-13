import asyncio
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager

from fastapi import FastAPI, Form, HTTPException
from pytubefix.exceptions import VideoUnavailable

from .db import collection
from .services.youtube import get_video_meta
from .worker import queue_loop

queue_task = None
meta_executor = ThreadPoolExecutor(max_workers=1)
META_TIMEOUT = 90


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

    try:
        loop = asyncio.get_running_loop()
        meta = await asyncio.wait_for(
            loop.run_in_executor(meta_executor, get_video_meta, link),
            timeout=META_TIMEOUT,
        )
    except asyncio.TimeoutError:
        print(f"⏱ YouTube is not responding: {link}")
        raise HTTPException(status_code=504, detail="YouTube is not responding right now. Please try again in a few minutes.")
    except VideoUnavailable:
        print(f"❌ Video is unavailable: {link}")
        raise HTTPException(status_code=404, detail="This YouTube video is unavailable.")
    except Exception as e:
        print(f"❌ Could not reach YouTube for {link}: {type(e).__name__}: {e}")
        raise HTTPException(status_code=502, detail="Could not reach YouTube right now. Please try again in a few minutes.")

    doc = {"link": link, "status": "queued", **meta}

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
