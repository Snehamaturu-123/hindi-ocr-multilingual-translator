# हिन्दी → English OCR Translator

A focused Hindi-to-English translator with OCR support — extract text from Hindi images and translate them to English in one click.

---

## 🧱 Project Structure

```
hindi_ocr_translator/
├── backend/
│   ├── app.py            ← FastAPI server (main entry point)
│   ├── model.py          ← NLLB-200 model loader (Hindi → English)
│   ├── translate.py      ← Translation logic
│   ├── ocr.py            ← Tesseract OCR for Hindi (Devanagari)
│   └── requirements.txt  ← Python dependencies
└── frontend/
    ├── index.html        ← Main UI
    ├── style.css         ← Styling
    └── script.js         ← Logic (OCR upload, translate, copy)
```

---

## ⚙️ Backend Setup

### 1. Install Tesseract OCR (System Package)

 Ubuntu / Debian: 
```bash
sudo apt update
sudo apt install tesseract-ocr tesseract-ocr-hin -y
```

 macOS: 
```bash
brew install tesseract
brew install tesseract-lang   # installs all language packs including Hindi
```

 Windows: 
- Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
- During install, check "Additional language data" → select  Hindi 
- Add Tesseract to your PATH

Verify installation:
```bash
tesseract --version
tesseract --list-langs  # should include 'hin'
```

---

### 2. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

> First run will download the NLLB-200 model (~2.4 GB). This only happens once.

---

### 3. Start the Backend Server

```bash
cd backend
uvicorn app:app --host 0.0.0.0 --port 8001 --reload
```

Server runs at: `http://localhost:8001`

---

## 🖥️ Frontend Setup

No build step needed. Just open the HTML file:

```bash
# Option 1: Direct open
open frontend/index.html

# Option 2: Serve locally (recommended to avoid CORS issues)
cd frontend
python -m http.server 5500
# then open http://localhost:5500
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/` | Health check |
| `POST` | `/ocr-and-translate` | Upload image → OCR → Translate (main flow) |
| `POST` | `/ocr` | Upload image → OCR only (returns Hindi text) |
| `POST` | `/translate/text` | Translate typed Hindi text to English |
| `POST` | `/translate/base64` | Send image as base64 → OCR → Translate |

### Example: Translate Text
```bash
curl -X POST http://localhost:8001/translate/text \
  -H "Content-Type: application/json" \
  -d '{"text": "नमस्ते, आप कैसे हैं?"}'
```

### Example: OCR + Translate Image
```bash
curl -X POST http://localhost:8001/ocr-and-translate \
  -F "file=@your_hindi_image.jpg"
```

---

## 📸 OCR Tips for Best Results

| ✅ Good Images | ❌ Avoid |
|---|---|
| Clear, high-contrast text | Blurry or pixelated |
| Printed text (books, signs) | Stylized/decorative fonts |
| Minimum 300 DPI | Very small text |
| Good lighting | Heavy shadows or glare |
| Flat/straight documents | Severely skewed pages |

---

## 🤖 Tech Stack

| Component | Technology |
|---|---|
| OCR Engine | Tesseract 5 + Hindi (`hin`) language pack |
| Translation Model | Facebook NLLB-200 (600M distilled) |
| Backend | FastAPI + Uvicorn |
| Image Processing | Pillow (PIL) |
| Frontend | Vanilla HTML/CSS/JS |

---

## 🔧 Troubleshooting

 `TesseractNotFoundError`  → Tesseract not in PATH. Set it manually in `ocr.py`:
```python
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

 `Error: Failed to load language 'hin'`  → Hindi language pack not installed:
```bash
sudo apt install tesseract-ocr-hin   # Linux
```

 Backend not reachable  → Make sure uvicorn is running on port 8001, and no firewall is blocking it.

 Poor OCR results  → Try a higher resolution image. You can also use image editing tools to increase contrast before uploading.


 ## 🔊 Features Added
- Backend-based multilingual Text-to-Speech (gTTS)
- Extended Indian language support via NLLB-200
- Improved language mapping system
