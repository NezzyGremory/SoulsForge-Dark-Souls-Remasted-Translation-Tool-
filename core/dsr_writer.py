import os
import sqlite3
import clr
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DLL_PATH = PROJECT_ROOT / "libs" / "SoulsFormats.dll"

if not DLL_PATH.exists():
    raise FileNotFoundError(f"DLL tidak ditemukan di: {DLL_PATH}")

clr.AddReference(str(DLL_PATH))
from SoulsFormats import BND3, BND4, FMG


def get_db_connection():
    db_path = PROJECT_ROOT / "data" / "translations.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def load_binder(input_path: Path):
    path_str = str(input_path)
    try:
        return BND4.Read(path_str)
    except Exception:
        return BND3.Read(path_str)


def process_dcx_file(input_path: Path, output_path: Path) -> None:
    file_name = input_path.name
    print(f"\n[Processing] Membuka berkas sumber: {file_name}")

    if not input_path.exists():
        print(f"[Error] Berkas {file_name} tidak ditemukan di folder input!")
        return

    bnd = load_binder(input_path)
    conn = get_db_connection()
    cursor = conn.cursor()

    updated_fmg_count = 0

    for file_entry in bnd.Files:
        if not file_entry.Name.endswith(".fmg"):
            continue

        fmg_filename = os.path.basename(file_entry.Name)
        fmg = FMG.Read(file_entry.Bytes)

        cursor.execute(
            """
            SELECT * 
            FROM translations 
            WHERE source_file = ? AND fmg_file = ?
        """,
            (file_name, fmg_filename),
        )

        rows = cursor.fetchall()
        if not rows:
            continue

        keys = rows[0].keys()
        
        # Deteksi otomatis nama kolom terjemahan yang ada di database
        trans_col = next(
            (k for k in ["text_translated", "translated_text", "text_id_str", "translation", "translated"] if k in keys),
            None
        )

        if not trans_col:
            ignored = {"id", "source_file", "fmg_file", "text_id", "text_en", "status"}
            candidates = [k for k in keys if k not in ignored]
            trans_col = candidates[0] if candidates else "text_en"

        trans_map = {}
        for row in rows:
            translated_val = row[trans_col] if trans_col in keys and row[trans_col] else row["text_en"]
            trans_map[row["text_id"]] = translated_val

        for entry in fmg.Entries:
            if entry.ID in trans_map and trans_map[entry.ID]:
                entry.Text = trans_map[entry.ID]

        file_entry.Bytes = fmg.Write()
        updated_fmg_count += 1

    conn.close()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    bnd.Write(str(output_path))
    print(f"[SUCCESS] Berhasil memperbarui {updated_fmg_count} FMG container di {file_name}")
    print(f"[OUTPUT] Berkas tersimpan di: {output_path}")


def run_writer() -> None:
    input_dir = PROJECT_ROOT / "input"
    output_dir = PROJECT_ROOT / "output"

    dcx_files = list(input_dir.glob("*.dcx"))

    if not dcx_files:
        print("[Warning] Tidak ada berkas .dcx ditemukan di folder input!")
        return

    print("=== Menjalankan DSR Writer (Batch All Files) ===")
    for dcx_file in dcx_files:
        out_file = output_dir / dcx_file.name
        process_dcx_file(dcx_file, out_file)

    print("\n[COMPLETE] Seluruh berkas DCX berhasil diproses dan dikompilasi!")


if __name__ == "__main__":
    run_writer()