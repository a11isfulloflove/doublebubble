import whisper

from ..config import WHISPER_LANGUAGE, WHISPER_MODEL

model = whisper.load_model(WHISPER_MODEL)


def transcribe_file(file_path: str) -> dict:
    return model.transcribe(file_path, verbose=False, language=WHISPER_LANGUAGE)
