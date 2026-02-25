import pytesseract
from PIL import Image
import io
import base64
import re
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_hindi_text_from_image(image_bytes: bytes) -> str:
    """
    Extract Hindi text from image bytes using Tesseract OCR.
    Uses Hindi (Devanagari) language pack.
    """
    # Reset stream and force full image load before stream closes
    stream = io.BytesIO(image_bytes)
    stream.seek(0)
    try:
        image = Image.open(stream)
        image.load()  # Force Pillow to fully decode image into memory
    except Exception as e:
        raise ValueError(
            f"Could not open image: {e}. "
            "Make sure the file is a valid JPG, PNG, or WebP."
        )

    # Convert to RGB (handles PNG with alpha channel, RGBA, palette mode, etc.)
    if image.mode != "RGB":
        image = image.convert("RGB")

    # Upscale small images — improves OCR accuracy significantly
    width, height = image.size
    if width < 1000:
        scale = 1000 / width
        new_size = (int(width * scale), int(height * scale))
        image = image.resize(new_size, Image.LANCZOS)

    # Run Tesseract with Hindi language pack
    # PSM 3 = Fully automatic page segmentation (best for general use)
    # OEM 3 = Default engine (LSTM + legacy)
    config = "--psm 3 --oem 3"
    extracted_text = pytesseract.image_to_string(image, lang="hin", config=config)

    return clean_ocr_output(extracted_text)


def clean_ocr_output(text: str) -> str:
    """Clean and normalize OCR output."""
    lines = text.split("\n")
    cleaned_lines = [line.strip() for line in lines if line.strip()]
    result = " ".join(cleaned_lines)

    # Keep only Devanagari Unicode range, punctuation, digits, spaces
    result = re.sub(r"[^\u0900-\u097F\s\d।,.!?;:()\-\"']", "", result)

    return result.strip()


def image_base64_to_bytes(base64_str: str) -> bytes:
    """Convert base64 image string to bytes."""
    # Strip data URL prefix if present (e.g., "data:image/png;base64,...")
    if "," in base64_str:
        base64_str = base64_str.split(",")[1]
    return base64.b64decode(base64_str)