import os
import sys

# Jalur ke SoulsFormats.dll
DLL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "libs", "SoulsFormats.dll"))

def load_souls_formats():
    if not os.path.exists(DLL_PATH):
        raise FileNotFoundError(f"DLL tidak ditemukan di: {DLL_PATH}")
    import clr
    clr.AddReference(DLL_PATH)
    import SoulsFormats  # type: ignore
    return SoulsFormats

def read_dsr_msgbnd(file_path):
    sf = load_souls_formats()
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Berkas tidak ditemukan: {file_path}")
    
    file_name_only = os.path.basename(file_path)
    print(f"\nMembaca berkas: {file_name_only}")
    
    # Dark Souls Remastered menggunakan kontainer BND3
    try:
        bnd = sf.BND3.Read(file_path)
    except Exception:
        # Fallback ke BND4 jika berkas menggunakan format BND4
        bnd = sf.BND4.Read(file_path)

    extracted_entries = []
    
    # Menelusuri berkas internal
    for file_entry in bnd.Files:
        if file_entry.Name.endswith(".fmg"):
            fmg_name = os.path.basename(file_entry.Name)
            fmg_data = file_entry.Bytes
            
            # Membaca tabel FMG
            fmg = sf.FMG.Read(fmg_data)
            
            print(f"  └─ [FMG Terdeteksi]: {fmg_name} | Jumlah Teks: {len(fmg.Entries)}")
            
            for entry in fmg.Entries:
                if entry.Text is not None and entry.Text.strip() != "":
                    extracted_entries.append({
                        "source_file": file_name_only,
                        "fmg_file": fmg_name,
                        "id": entry.ID,
                        "text": entry.Text
                    })
                    
    return extracted_entries

if __name__ == "__main__":
    input_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "input"))
    all_results = []
    
    msgbnd_files = [f for f in os.listdir(input_dir) if f.endswith(".msgbnd.dcx")]
    
    if not msgbnd_files:
        print(f"[ERROR] Tidak ada berkas .msgbnd.dcx di folder: {input_dir}")
    else:
        try:
            for file_name in msgbnd_files:
                file_path = os.path.join(input_dir, file_name)
                entries = read_dsr_msgbnd(file_path)
                all_results.extend(entries)
                
            print(f"\n==========================================")
            print(f"[SUCCESS] Total entri teks terbaca dari {len(msgbnd_files)} berkas: {len(all_results)}")
            print(f"==========================================")
            
            print("\n--- Sampel 5 Teks Pertama ---")
            for sample in all_results[:5]:
                print(f"[{sample['source_file']} -> {sample['fmg_file']}] ID: {sample['id']} -> {sample['text']}")
                
        except Exception as e:
            print(f"[ERROR] {e}")