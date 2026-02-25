from model import tokenizer, model, device

SUPPORTED_LANGUAGES = {
    "eng_Latn": "English",
    "hin_Deva": "Hindi",
    "tam_Taml": "Tamil",
    "tel_Telu": "Telugu",
    "kan_Knda": "Kannada",
    "mal_Mlym": "Malayalam",
    "mar_Deva": "Marathi",
    "ben_Beng": "Bengali",
    "guj_Gujr": "Gujarati",
    "pan_Guru": "Punjabi",
    "urd_Arab": "Urdu",
    "ory_Orya": "Odia",
    "asm_Beng": "Assamese",
    "mai_Deva": "Maithili",
    "san_Deva": "Sanskrit",
    "snd_Arab": "Sindhi",
    "kas_Arab": "Kashmiri",
    "mni_Beng": "Manipuri"
}


def translate_text(text: str, src_lang: str, tgt_lang: str) -> str:

    if tgt_lang not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported target language: {tgt_lang}")

    tokenizer.src_lang = src_lang

    inputs = tokenizer(
        text,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=512
    ).to(device)

    tgt_lang_id = tokenizer.convert_tokens_to_ids(tgt_lang)

    outputs = model.generate(
        **inputs,
        forced_bos_token_id=tgt_lang_id,
        max_length=512
    )

    return tokenizer.decode(outputs[0], skip_special_tokens=True)