import sqlite3
import os

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "translations.db"))

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS translations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_file TEXT,
            fmg_file TEXT,
            text_id INTEGER,
            text_en TEXT,
            text_id_lang TEXT,
            status TEXT DEFAULT 'pending',
            UNIQUE(source_file, fmg_file, text_id)
        )
    """)
    conn.commit()
    conn.close()

def save_entries(entries):
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    
    inserted = 0
    for entry in entries:
        cursor.execute("""
            INSERT OR IGNORE INTO translations (source_file, fmg_file, text_id, text_en, status)
            VALUES (?, ?, ?, ?, 'pending')
        """, (entry['source_file'], entry['fmg_file'], entry['id'], entry['text']))
        if cursor.rowcount > 0:
            inserted += 1
            
    conn.commit()
    conn.close()
    return inserted

def get_pending_translations(limit=20):
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, source_file, fmg_file, text_id, text_en 
        FROM translations 
        WHERE status = 'pending' AND text_en IS NOT NULL AND TRIM(text_en) != ''
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_translation(entry_id, text_id_lang):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE translations 
        SET text_id_lang = ?, status = 'translated' 
        WHERE id = ?
    """, (text_id_lang, entry_id))
    conn.commit()
    conn.close()

def get_stats():
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM translations")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM translations WHERE status = 'translated'")
    translated = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM translations WHERE status = 'pending'")
    pending = cursor.fetchone()[0]
    
    conn.close()
    return {"total": total, "translated": translated, "pending": pending}

if __name__ == "__main__":
    init_db()
    print("[OK] Database tersinkronisasi:", get_stats())