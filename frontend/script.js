const API = "http://localhost:8001";

let currentFile = null;

// Language display names (matches the select values)
const LANG_NAMES = {
  "eng_Latn": "English",
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
  "mni_Beng": "Manipuri",
  "npi_Deva": "Nepali",
  "kok_Deva": "Konkani",
  "dgo_Deva": "Dogri",
};

// Short badge labels (2-3 chars)
const LANG_BADGES = {
  "eng_Latn": "EN",
  "tam_Taml": "TA",
  "tel_Telu": "TE",
  "kan_Knda": "KA",
  "mal_Mlym": "ML",
  "mar_Deva": "MR",
  "ben_Beng": "BN",
  "guj_Gujr": "GU",
  "pan_Guru": "PA",
  "urd_Arab": "UR",
  "ory_Orya": "OR",
  "asm_Beng": "AS",
  "mai_Deva": "MAI",
  "san_Deva": "SA",
  "snd_Arab": "SN",
  "kas_Arab": "KS",
  "mni_Beng": "MN",
  "npi_Deva": "NE",
  "kok_Deva": "KOK",
  "dgo_Deva": "DG",
};

// ── Language change handler ───────────────────────────────────────────────────
function onLangChange() {
  const code = getTargetLang();
  const name = LANG_NAMES[code] || code;

  // Update header
  document.getElementById("headerTarget").textContent = name;

  // Clear previous results
  document.getElementById("ocrResult").style.display = "none";
  document.getElementById("textResult").style.display = "none";
}

function getTargetLang() {
  return document.getElementById("targetLang").value;
}

function updateResultBadge(ocrOrText) {
  const code = getTargetLang();
  const name = LANG_NAMES[code] || code;
  const badge = LANG_BADGES[code] || code.substring(0, 2).toUpperCase();

  document.getElementById(`${ocrOrText}ResultBadge`).textContent = badge;
  document.getElementById(`${ocrOrText}ResultLangName`).textContent = name;
}

// ── Mode Switching ────────────────────────────────────────────────────────────
function switchMode(mode) {
  document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
  document.querySelectorAll(".mode-section").forEach(s => s.classList.remove("active"));

  document.querySelector(`[data-mode="${mode}"]`).classList.add("active");
  document.getElementById(`${mode}-mode`).classList.add("active");

  // 🔥 Hide shared language bar in text mode
  const sharedBar = document.getElementById("sharedLangBar");

  if (mode === "text") {
    sharedBar.style.display = "none";
  } else {
    sharedBar.style.display = "flex";
  }
}

// ── Drag & Drop ───────────────────────────────────────────────────────────────
function handleDragOver(e) {
  e.preventDefault();
  document.getElementById("dropZone").classList.add("dragover");
}

function handleDragLeave() {
  document.getElementById("dropZone").classList.remove("dragover");
}

function handleDrop(e) {
  e.preventDefault();
  document.getElementById("dropZone").classList.remove("dragover");
  const file = e.dataTransfer.files[0];
  if (file && file.type.startsWith("image/")) {
    loadImageFile(file);
  } else {
    showToast("Please drop an image file (JPG, PNG, WebP)", "error");
  }
}

function handleFileSelect(e) {
  const file = e.target.files[0];
  if (file) loadImageFile(file);
}

function loadImageFile(file) {
  currentFile = file;
  const reader = new FileReader();
  reader.onload = (e) => {
    const preview = document.getElementById("imagePreview");
    preview.src = e.target.result;
    preview.classList.add("visible");

    document.getElementById("dropZone").classList.add("has-image");
    document.getElementById("dropIcon").style.display = "none";
    document.getElementById("dropMain").style.display = "none";

    document.getElementById("ocrTranslateBtn").style.display = "flex";
    document.getElementById("ocrExtractedGroup").style.display = "none";
    document.getElementById("ocrResult").style.display = "none";
  };
  reader.readAsDataURL(file);
}

// ── OCR + Translate ───────────────────────────────────────────────────────────
async function runOCRAndTranslate() {
  if (!currentFile) {
    showToast("Please upload an image first", "error");
    return;
  }

  const targetLang = getTargetLang();
  const btn = document.getElementById("ocrTranslateBtn");
  setButtonLoading(btn, true);

  try {
    const formData = new FormData();
    formData.append("file", currentFile);

    const response = await fetch(`${API}/ocr-and-translate?target_lang=${targetLang}`, {
      method: "POST",
      body: formData
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || "Server error");
    }

    const data = await response.json();

    if (data.warning) {
      showToast(data.warning, "error");
      return;
    }

    // Show extracted text
    document.getElementById("ocrExtracted").value = data.extracted_text;
    document.getElementById("ocrExtractedGroup").style.display = "flex";

    // Show translation with correct language label
    updateResultBadge("ocr");
    document.getElementById("ocrTranslation").textContent = data.translation;
    document.getElementById("ocrResult").style.display = "block";

    showToast(`Translated to ${data.target_lang_name} ✓`, "success");

  } catch (err) {
    console.error(err);
    showToast(
      err.message.includes("fetch")
        ? "Cannot reach backend. Is it running on port 8001?"
        : "Error: " + err.message,
      "error"
    );
  } finally {
    setButtonLoading(btn, false);
  }
}

// ── Typed Text Translation ────────────────────────────────────────────────────
async function translateTyped() {

    const text = document.getElementById("textInput").value;
    const sourceLang = document.getElementById("sourceLang").value;
    const targetLang = document.getElementById("textTargetLang").value;

    if (!text.trim()) {
        showToast("Please enter text", "error");
        return;
    }

    document.getElementById("textLoader").style.display = "inline-block";

    try {
        const response = await fetch(`${API}/translate_text`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                text: text,
                source_lang: sourceLang,
                target_lang: targetLang
            })
        });

        const data = await response.json();

        document.getElementById("textLoader").style.display = "none";
        document.getElementById("textResult").style.display = "block";
        document.getElementById("textTranslation").innerText = data.translated_text;

    } catch (error) {
        console.error(error);
        showToast("Translation failed", "error");
        document.getElementById("textLoader").style.display = "none";
    }
}

// ── Edit OCR Output ───────────────────────────────────────────────────────────
function enableOcrEdit() {
  const textarea = document.getElementById("ocrExtracted");
  const editBtn = document.getElementById("ocrEditBtn");

  textarea.removeAttribute("readonly");
  textarea.style.color = "var(--text)";
  textarea.focus();

  editBtn.textContent = "Re-translate";
  editBtn.onclick = async () => {
    const newText = textarea.value.trim();
    if (!newText) return;

    const targetLang = getTargetLang();
    try {
      const response = await fetch(`${API}/translate/text`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: newText, target_lang: targetLang })
      });
      const data = await response.json();

      updateResultBadge("ocr");
      document.getElementById("ocrTranslation").textContent = data.translation;
      document.getElementById("ocrResult").style.display = "block";

      textarea.setAttribute("readonly", true);
      textarea.style.color = "";
      editBtn.textContent = "Edit";
      editBtn.onclick = enableOcrEdit;

      showToast(`Re-translated to ${data.target_lang_name} ✓`, "success");
    } catch (err) {
      showToast("Re-translation failed", "error");
    }
  };
}

// ── Char Counter ──────────────────────────────────────────────────────────────
document.getElementById("hindiInput")?.addEventListener("input", function () {
  const n = this.value.length;
  document.getElementById("charCount").textContent = `${n} character${n !== 1 ? "s" : ""}`;
});

// ── Helpers ───────────────────────────────────────────────────────────────────
function setButtonLoading(btn, loading) {
  const text = btn.querySelector(".btn-text");
  const loader = btn.querySelector(".btn-loader");
  btn.disabled = loading;
  if (text) text.style.display = loading ? "none" : "inline";
  if (loader) loader.style.display = loading ? "flex" : "none";
}

function copyText(elementId) {
  const text = document.getElementById(elementId).textContent;
  navigator.clipboard.writeText(text).then(() => showToast("Copied ✓", "success"));
}

let toastTimer;
function showToast(message, type = "") {
  const toast = document.getElementById("toast");
  toast.textContent = message;
  toast.className = `toast ${type} show`;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove("show"), 3000);
}