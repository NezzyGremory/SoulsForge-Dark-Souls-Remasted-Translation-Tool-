import time
from deep_translator import GoogleTranslator
from db_manager import get_pending_translations, update_translation

def safe_translate_single(translator, text):
    """Menerjemahkan 1 teks. Jika > 3000 karakter (seperti EULA), dipotong per 2000 karakter."""
    if not text or not text.strip():
        return text
    
    if len(text) > 3000:
        # Potong teks raksasa menjadi potongan 2000 karakter
        chunks = [text[i:i+2000] for i in range(0, len(text), 2000)]
        translated_chunks = []
        for chunk in chunks:
            try:
                translated_chunks.append(translator.translate(chunk))
                time.sleep(0.3)
            except Exception:
                translated_chunks.append(chunk)
        return "".join(translated_chunks)
    else:
        return translator.translate(text)

def run_smart_bulk_translator():
    translator = GoogleTranslator(source='en', target='id')
    print("=== Menjalankan Google Translator (Aman Teks Panjang/EULA) ===")
    
    total_translated = 0
    DELIMITER = " ||| "
    MAX_CHAR_LIMIT = 1200

    while True:
        candidates = get_pending_translations(limit=30)
        if not candidates:
            print("\n[OK] Semua teks di database SUDAH SELESAI diterjemahkan!")
            break

        pending_entries = []
        current_length = 0
        has_huge_text = False

        for entry in candidates:
            text = entry["text_en"] or ""
            clean_text = text.replace("\n", " [BR] ")
            text_len = len(clean_text)

            # Jika menemukan 1 teks raksasa (seperti EULA)
            if text_len > MAX_CHAR_LIMIT:
                if not pending_entries:
                    print(f"└─ Menerjemahkan teks panjang/EULA ({text_len} karakter)...", flush=True)
                    try:
                        trans = safe_translate_single(translator, entry["text_en"])
                        update_translation(entry["id"], trans)
                        total_translated += 1
                        print(f"└─ Terproses tambahan: {total_translated} teks...", flush=True)
                    except Exception as e:
                        print(f"└─ [Gagal Teks Panjang]: {e}. Lewati...", flush=True)
                    has_huge_text = True
                    break
                else:
                    break

            if current_length + text_len + len(DELIMITER) <= MAX_CHAR_LIMIT:
                pending_entries.append(entry)
                current_length += text_len + len(DELIMITER)
            else:
                break

        if has_huge_text:
            continue

        if not pending_entries:
            break

        clean_texts = [e["text_en"].replace("\n", " [BR] ") if e["text_en"] else "" for e in pending_entries]
        combined_text = DELIMITER.join(clean_texts)

        try:
            translated_combined = translator.translate(combined_text)
            
            if not translated_combined:
                raise Exception("Respon kosong")

            translated_list = translated_combined.split("|||")

            if len(translated_list) == len(pending_entries):
                for entry, trans_text in zip(pending_entries, translated_list):
                    final_text = trans_text.replace("[BR]", "\n").strip()
                    update_translation(entry["id"], final_text)
                    total_translated += 1
            else:
                for entry in pending_entries:
                    if entry["text_en"]:
                        t = safe_translate_single(translator, entry["text_en"])
                    else:
                        t = ""
                    update_translation(entry["id"], t)
                    total_translated += 1

            print(f"└─ Terproses tambahan: {total_translated} teks...", flush=True)
            time.sleep(0.3)

        except Exception as e:
            print(f"└─ [Koneksi Renggang]: {e}. Menunggu 3 detik...", flush=True)
            time.sleep(3)

    print(f"\n[SELESAI] Total teks baru berhasil diterjemahkan: {total_translated}")

if __name__ == "__main__":
    run_smart_bulk_translator()