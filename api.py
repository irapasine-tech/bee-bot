from fastapi import FastAPI
import sqlite3
from datetime import datetime

app = FastAPI()

conn = sqlite3.connect("hives.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS records (
    hive INTEGER,
    text TEXT,
    score INTEGER,
    time TEXT
)
""")
conn.commit()


def score(text):
    t = text.lower()
    s = 50
    if "расплод" in t: s += 15
    if "мёд" in t: s += 10
    if "агресс" in t: s -= 25
    return max(0, min(100, s))


@app.post("/add")
def add_record(hive: int, text: str):
    s = score(text)
    cur.execute("INSERT INTO records VALUES (?, ?, ?, ?)",
                (hive, text, s, datetime.now().isoformat()))
    conn.commit()
    return {"status": "ok", "score": s}


@app.get("/hives")
def get_hives():
    cur.execute("SELECT hive, score FROM records")
    return cur.fetchall()
