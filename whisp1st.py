import os
import tempfile
import aiofiles
import shutil
import whisper
from fastapi import FastAPI, Form, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
import requests
import base64
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from concurrent.futures import ThreadPoolExecutor

from transformers import MarianMTModel, MarianTokenizer

from pytubefix import YouTube
from pytubefix.cli import on_progress
from pytubefix.exceptions import VideoUnavailable

#создать окружение:
#python3 -m venv .venv
#source .venv/bin/activate
#установить зависимости:
#python3 -m pip install -r requirements.txt 
#запустить:
#python3 -m uvicorn whisp1st:app

app = FastAPI()
model = whisper.load_model("medium")  #"small" / "medium" / "large" 
executor = ThreadPoolExecutor(max_workers=1) 

model_name = 'Helsinki-NLP/opus-mt-ko-en' # Korean (ko) to English (en)
tokenizer = MarianTokenizer.from_pretrained(model_name)
model_tr = MarianMTModel.from_pretrained(model_name)

client = AsyncIOMotorClient("mongodb://localhost:27017/")
db = client["dubsub"]
collection = db["subs"]

worker_running = False


def transcribe_file(file_path):
    result = model.transcribe(file_path, verbose=False, language="ko")
    return result

def translate_file(src_text):
    inputs = tokenizer(src_text, return_tensors="pt", padding=True)
    translated = model_tr.generate(**inputs)
    tgt_text = [tokenizer.decode(t, skip_special_tokens=True) for t in translated]
    return tgt_text[0] if tgt_text else ""

def download_audio(url):
    yt = YouTube(url, on_progress_callback=on_progress)

    vidtitle = yt.title
    ys = yt.streams.get_highest_resolution()

    lala = yt.streams.get_audio_only()
    return lala.download()

def slug_title(text: str) -> str:
    return "-".join(text.split())

async def process_transcription(link: str):
    yt = YouTube(link)
    downloaded_path = yt.streams.get_audio_only().download(
        output_path="/Users/tiny/Documents/whisper",
        filename=yt.title + ".m4a"
    )

    suffix = os.path.splitext(downloaded_path)[-1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp_path = tmp.name

    async with aiofiles.open(downloaded_path, 'rb') as source_file:
        async with aiofiles.open(tmp_path, 'wb') as dest_file:
            while chunk := await source_file.read(1024 * 1024):
                await dest_file.write(chunk)

    loop = asyncio.get_running_loop()
    try:
        result = await loop.run_in_executor(executor, transcribe_file, tmp_path)
    finally:
        os.remove(tmp_path)
        os.remove(downloaded_path)

    response = [
        {
            'start': seg['start'],
            'end': seg['end'],
            'text': seg['text'],
            'tr': translate_file(seg['text'])
        }
        for seg in result['segments']
    ]

    await collection.update_one(
        {"link": link},
        {"$set": {
            "segments": response,
            "language": result.get("language", "unknown"),
            "full_text": result.get("text", ""),
            "status": "done",
        }}
    )

    print(f"Transcription for {link} finished.")

async def queue_loop():
    print("🚀 Цикл очереди запущен")
    while True:
        processing_now = await collection.find_one({"status": "processing"})
        if processing_now:
            await asyncio.sleep(5)
            continue

        next_video = await collection.find_one({"status": "queued"})
        if not next_video:
            print("⏸ Очередь пуста, пауза...")
            await asyncio.sleep(5)
            continue
        
        if next_video:
            link_to_process = next_video["link"]

        await collection.update_one(
            {"link": link_to_process},
            {"$set": {"status": "processing"}}
        )

        try:
            await process_transcription(link_to_process)
        except Exception as e:
            print(f"❌ Ошибка при обработке {link_to_process}: {e}")
            await collection.update_one(
                {"link": link_to_process},
                {"$set": {"status": "error", "error": str(e)}}
            )

        await asyncio.sleep(2)

@app.post("/transcribe")
async def transcribe(link: str = Form(...)):
    print(f"link: {link}")

    existing = await collection.find_one({"link": link})
    
    if existing:
        if existing.get("status") == "queued":
            return {"status": "queued", "message": "This video is already in the queue"}
        if existing.get("status") == "processing":
            return {"status": "processing", "message": "This video is already being processed"}
        elif existing.get("status") == "done":
            return {"status": "done", "message": "This video already exists. Please!! check the feed"}

    try:
        yt = YouTube(link, on_progress_callback=on_progress)
        title = yt.title
        thumbnail_url = yt.thumbnail_url

    except VideoUnavailable:
        print(f"❌ Video is unavailable: {link}")
        raise HTTPException(
            status_code=404,
            detail="This YouTube video is unavailable."
    )

    response_img = requests.get(thumbnail_url)
    thumbnail_bytes = response_img.content
    thumbnail_base64 = base64.b64encode(thumbnail_bytes).decode("utf-8")

    doc = {
        "title": title,
        "slug": slug_title(title),
        "link": link,
        "thumbnail_base64": thumbnail_base64,
        "status": "queued",  # <-- статус загрузки
    }

    await collection.insert_one(doc)
    await queue_loop()


@app.get("/getallvideos")
async def get_subs():
    cursor = collection.find({}, {"_id": 0, "link": 1, "title": 1, "slug": 1, "thumbnail_base64": 1, "status": 1})
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
