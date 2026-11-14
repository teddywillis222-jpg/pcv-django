import sqlite3

conn = sqlite3.connect('db.sqlite3')
cur = conn.cursor()

tables = [row[0] for row in cur.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()]
print("Tables in sqlite:", [t for t in tables if 'teacher' in t.lower() or 'user' in t.lower()])

cur.execute("SELECT count(*) FROM core_teacherprofile;")
print("Count in core_teacherprofile (sqlite):", cur.fetchone()[0])
conn.close()
