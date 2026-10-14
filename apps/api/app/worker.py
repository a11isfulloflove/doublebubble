import asyncio
import os
import tempfile
from concurrent.futures import ThreadPoolExecutor

import aiofiles

from .config import DOWNLOAD_DIR, QUEUE_POLL_INTERVAL
from .db import collection
from .services.transcription import transcribe_file
from .services.translation import translate_file
from .services.youtube import download_audio, get_video_meta

executor = ThreadPoolExecutor(max_workers=1)


async def process_transcription(link: str):
    meta = await asyncio.get_running_loop().run_in_executor(
        executor, get_video_meta, link
    )
    await collection.update_one({"link": link}, {"$set": meta})

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    downloaded_path = await asyncio.get_running_loop().run_in_executor(
        executor, download_audio, link, DOWNLOAD_DIR
    )

    suffix = os.path.splitext(downloaded_path)[-1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp_path = tmp.name

    async with aiofiles.open(downloaded_path, "rb") as source_file:
        async with aiofiles.open(tmp_path, "wb") as dest_file:
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
            "start": seg["start"],
            "end": seg["end"],
            "text": seg["text"],
            "tr": translate_file(seg["text"]),
        }
        for seg in result["segments"]
    ]

    await collection.update_one(
        {"link": link},
        {"$set": {
            "segments": response,
            "language": result.get("language", "unknown"),
            "full_text": result.get("text", ""),
            "status": "done",
        }},
    )

    print(f"Transcription for {link} finished.")


async def queue_loop():
    print("🚀 Цикл очереди запущен")
    while True:
        processing_now = await collection.find_one({"status": "processing"})
        if processing_now:
            await asyncio.sleep(QUEUE_POLL_INTERVAL)
            continue

        next_video = await collection.find_one({"status": "queued"})
        if not next_video:
            print("⏸ Очередь пуста, пауза...")
            await asyncio.sleep(QUEUE_POLL_INTERVAL)
            continue

        link_to_process = next_video["link"]

        await collection.update_one(
            {"link": link_to_process},
            {"$set": {"status": "processing"}},
        )

        try:
            await process_transcription(link_to_process)
        except Exception as e:
            print(f"❌ Ошибка при обработке {link_to_process}: {e}")
            await collection.update_one(
                {"link": link_to_process},
                {"$set": {"status": "error", "error": str(e)}},
            )

        await asyncio.sleep(2)
