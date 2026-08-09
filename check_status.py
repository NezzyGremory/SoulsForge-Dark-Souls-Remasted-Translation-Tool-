import sqlite3

conn = sqlite3.connect('data/translations.db')
cursor = conn.cursor()

translated = cursor.execute("SELECT COUNT(1) FROM translations WHERE status='translated'").fetchone()[0]
pending = cursor.execute("SELECT COUNT(1) FROM translations WHERE status='pending'").fetchone()[0]

print("\n--- STATUS TRANSLATION DATABASE ---")
print(f"Total SUDAH DITERJEMAHKAN : {translated}")
print(f"Total MASIH PENDING       : {pending}")
print("-----------------------------------\n")

conn.close()