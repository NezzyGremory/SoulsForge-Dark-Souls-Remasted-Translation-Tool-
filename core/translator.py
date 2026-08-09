import json
import os
import time
import warnings

# Menyembunyikan peringatan deprecation SDK
warnings.filterwarnings("ignore", category=FutureWarning)

import google.generativeai as genai  # type: ignore
from db_manager import get_pending_translations, update_translation

# Jalur menuju config.json
CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config.json"))

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

config = load_config()
api_key = config.get("gemini_api_key", "").strip()

if not api_key:
    raise ValueError("GEMINI_API_KEY belum diisi di berkas config.json! Silakan buka config.json dan masukkan API Key Anda.")

# Konfigurasi Gemini API menggunakan API Key dari config.json
genai.configure(api_key=api_key)
model_name = config.get("model_name", "gemini-2.5-flash")
model = genai.GenerativeModel(model_name)

def translate_batch(entries):
    if not entries:
        return 0

    source_lang = config.get("source_language", "English")
    target_lang = config.get("target_language", "Indonesian")

    prompt = f"Translate the following texts from {source_lang} to {target_lang} for Dark Souls Remastered modding.\n"
    prompt += "Maintain tone, style, and formatting (like line breaks or placeholders).\n"
    prompt += "Output ONLY a JSON array of strings in the exact same order as input.\n\n"
    
    texts_to_translate = [e["text_en"] for e in entries]
    prompt += json.dumps(texts_to_translate, ensure_ascii=False)

    try:
        response = model.generate_content(prompt)
        raw_text = response.text.strip()
        
        # Format pembersihan JSON response
        if raw_text.startswith("```json"):
            raw_text = raw_text.replace("```json", "", 1).rsplit("```", 1)[0].strip()
        elif raw_text.startswith("```"):
            raw_text = raw_text.replace("```", "", 1).rsplit("```", 1)[0].strip()

        translated_list = json.loads(raw_text)

        if len(translated_list) != len(entries):
            print(f"[WARN] Jumlah hasil ({len(translated_list)}) berbeda dari input ({len(entries)}). Batch dilewati.")
            return 0

        success_count = 0
        for entry, trans_text in zip(entries, translated_list):
            update_translation(entry["id"], trans_text)
            success_count += 1

        return success_count

    except Exception as e:
        print(f"[ERROR Gemini API]: {e}")
        return 0

def run_translation_loop(batch_size=None, delay_seconds=2):
    if batch_size is None:
        batch_size = config.get("batch_size", 20)

    print(f"=== Menjalankan Translator (Model: {model_name}) ===")
    
    total_translated = 0
    while True:
        pending_entries = get_pending_translations(limit=batch_size)
        if not pending_entries:
            print("\n[OK] Semua teks sudah selesai diterjemahkan!")
            break

        print(f"Menerjemahkan batch ({len(pending_entries)} teks)...")
        count = translate_batch(pending_entries)
        total_translated += count
        print(f"  └─ Berhasil menerjemahkan {count}/{len(pending_entries)} teks.")

        time.sleep(delay_seconds)

    print(f"\n[SELESAI] Total teks diterjemahkan pada sesi ini: {total_translated}")

if __name__ == "__main__":
    # delay_seconds=5 
    run_translation_loop(delay_seconds=5)