import json
import os
import sys

def verify_environment():
    print("=== SoulForge: Inisialisasi Environment ===")
    print(f"Versi Python: {sys.version.split()[0]}")
    
    # 1. Cek keberadaan folder penting
    required_folders = ["core", "api", "ui", "data", "libs", "input", "output", "backups", "logs"]
    missing_folders = []
    
    for folder in required_folders:
        if not os.path.exists(folder):
            missing_folders.append(folder)
            
    if missing_folders:
        print(f"[ERROR] Folder berikut tidak ditemukan: {missing_folders}")
        return False
    print("[OK] Semua direktori proyek terdeteksi.")

    # 2. Cek berkas konfigurasi
    if not os.path.exists("config.json"):
        print("[ERROR] Berkas config.json tidak ditemukan!")
        return False
        
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
            print("[OK] Berkas config.json berhasil dibaca.")
    except Exception as e:
        print(f"[ERROR] Gagal membaca config.json: {e}")
        return False

    print("\nEnvironment siap. Proyek SoulForge siap dilanjutkan ke Milestone 2.")
    return True

if __name__ == "__main__":
    verify_environment()