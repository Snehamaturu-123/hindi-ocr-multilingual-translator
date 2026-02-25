from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from translate import translate_text, SUPPORTED_LANGUAGES
from ocr import extract_hindi_text_from_image, image_base64_to_bytes
from fastapi.responses import StreamingResponse
from io import BytesIO
from gtts import gTTS

TTS_LANGUAGE_MAP = {
    "eng_Latn": "en",
    "hin_Deva": "hi",
    "tam_Taml": "ta",
    "tel_Telu": "te",
    "kan_Knda": "kn",
    "mal_Mlym": "ml",
    "mar_Deva": "mr",
    "ben_Beng": "bn",
    "guj_Gujr": "gu",
    "pan_Guru": "pa",
    "urd_Arab": "ur",
    "ory_Orya": "or",
    "asm_Beng": "as",
}


app = FastAPI(title="Hindi → Any Language OCR Translator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Request Models ───────────────────────────────────────────────────────────

class TextRequest(BaseModel):
    text: str
    target_lang: str = "eng_Latn"   # default to English


class Base64ImageRequest(BaseModel):
    image_base64: str
    target_lang: str = "eng_Latn"


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "Hindi → Any Language OCR Translator API 🚀"}


@app.get("/languages")
def get_languages():
    """Return all supported target languages."""
    return {
        "source": {"code": "hin_Deva", "name": "Hindi"},
        "targets": [
            {"code": code, "name": name}
            for code, name in SUPPORTED_LANGUAGES.items()
        ]
    }

@app.post("/translate_text")
async def translate_text_api(data: dict):

    text = data.get("text")
    source_lang = data.get("source_lang")
    target_lang = data.get("target_lang")

    translated = translate_text(text, source_lang, target_lang)

    return {"translated_text": translated}
    
@app.post("/ocr")
async def ocr_image(file: UploadFile = File(...)):
    """Upload a Hindi image → extract text via OCR (no translation)."""
    if file.content_type and not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    try:
        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")
        print(f"📷 /ocr received {len(image_bytes)} bytes")
        extracted_text = extract_hindi_text_from_image(image_bytes)
        if not extracted_text:
            return {"extracted_text": "", "warning": "No Hindi text detected in image"}
        return {"extracted_text": extracted_text}
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ OCR error: {e}")
        raise HTTPException(status_code=500, detail=f"OCR failed: {str(e)}")


@app.post("/ocr-and-translate")
async def ocr_and_translate(
    file: UploadFile = File(...),
    target_lang: str = "eng_Latn"     # query param: ?target_lang=tam_Taml
):
    """
    Full pipeline: Upload Hindi image → OCR → Translate to chosen language.
    Pass target_lang as a query parameter: /ocr-and-translate?target_lang=tam_Taml
    """
    if file.content_type and not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    if target_lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unsupported target language: {target_lang}")
    try:
        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")
        print(f"📷 /ocr-and-translate received {len(image_bytes)} bytes → target: {target_lang}")

        # Step 1: OCR
        extracted_text = extract_hindi_text_from_image(image_bytes)
        if not extracted_text:
            return {
                "extracted_text": "",
                "translation": "",
                "warning": "No Hindi text detected in image. Please use a clearer image."
            }

        # Step 2: Translate
        translation = translate_text(extracted_text, "hin_Deva", target_lang)
        return {
            "extracted_text": extracted_text,
            "translation": translation,
            "target_lang": target_lang,
            "target_lang_name": SUPPORTED_LANGUAGES[target_lang]
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ OCR+Translate error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/translate/base64")
def translate_base64_image(req: Base64ImageRequest):
    """Send image as base64 → OCR → Translate to chosen language."""
    if req.target_lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unsupported target language: {req.target_lang}")
    try:
        image_bytes = image_base64_to_bytes(req.image_base64)
        extracted_text = extract_hindi_text_from_image(image_bytes)
        if not extracted_text:
            return {"extracted_text": "", "translation": "", "warning": "No text detected"}
        translation = translate_text(extracted_text, req.target_lang)
        return {
            "extracted_text": extracted_text,
            "translation": translation,
            "target_lang": req.target_lang,
            "target_lang_name": SUPPORTED_LANGUAGES[req.target_lang]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/speak")
async def generate_speech(data: dict):
    text = data.get("text")
    lang_code = data.get("lang")

    if not text:
        raise HTTPException(status_code=400, detail="Text is required")

    tts_lang = TTS_LANGUAGE_MAP.get(lang_code)

    if not tts_lang:
        raise HTTPException(status_code=400, detail="TTS not supported for this language")

    try:
        tts = gTTS(text=text, lang=tts_lang)

        mp3_fp = BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)

        return StreamingResponse(mp3_fp, media_type="audio/mpeg")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))