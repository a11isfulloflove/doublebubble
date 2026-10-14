from transformers import MarianMTModel, MarianTokenizer

from ..config import TRANSLATION_MODEL

tokenizer = MarianTokenizer.from_pretrained(TRANSLATION_MODEL)
model = MarianMTModel.from_pretrained(TRANSLATION_MODEL)


def translate_file(src_text: str) -> str:
    inputs = tokenizer(src_text, return_tensors="pt", padding=True)
    translated = model.generate(**inputs)
    tgt_text = [tokenizer.decode(t, skip_special_tokens=True) for t in translated]
    return tgt_text[0] if tgt_text else ""
