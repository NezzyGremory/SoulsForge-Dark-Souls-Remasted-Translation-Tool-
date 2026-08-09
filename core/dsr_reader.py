import os
import sys

# Jalur mutlak menuju SoulsFormats.dll di folder libs
DLL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "libs", "SoulsFormats.dll"))

def load_souls_formats():
    if not os.path.exists(DLL_PATH):
        raise FileNotFoundError(f"Berkas DLL tidak ditemukan di: {DLL_PATH}")
    
    try:
        import clr
        # Memuat DLL .NET ke dalam runtime Python
        clr.AddReference(DLL_PATH)
        
        # Mengimpor modul utama SoulsFormats
        import SoulsFormats  # type: ignore
        return SoulsFormats
    except Exception as e:
        raise RuntimeError(f"Gagal memuat SoulsFormats.dll: {e}")

if __name__ == "__main__":
    try:
        sf = load_souls_formats()
        print("[OK] SoulsFormats.dll berhasil dimuat oleh Python!")
        print(f"Modul terdeteksi: {sf.SoulsFile}")
    except Exception as err:
        print(f"[ERROR] {err}")