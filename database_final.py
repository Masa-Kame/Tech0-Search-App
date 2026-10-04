import sqlite3
from pathlib import Path
from datetime import datetime

# DB ファイルのパス（data/ サブフォルダに保存する）
DB_PATH = Path("data/tech0_search.db")

def get_connection():
    DB_PATH.parent.mkdir(exist_ok=True)   # data/ フォルダがなければ作る
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row        # 行データを辞書のように扱う
    return conn

def init_db():
    conn = get_connection()
    with open("schema_me.sql", "r", encoding="utf-8") as f:
        conn.executescript(f.read())    # SQL ファイルをまとめて実行する
    conn.commit()
    conn.close()

def _keywords_to_text(keywords) -> str:
    if not keywords:
        return ""
    if isinstance(keywords, str):
        return keywords
    return ",".join(keywords)

def insert_page(page: dict) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO pages
            (url, title, description, full_text, author, category, keywords, word_count, crawled_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        page["url"],
        page["title"],
        page.get("description", ""),
        page.get("full_text", ""),
        page.get("author", ""),
        page.get("category", ""),
        _keywords_to_text(page.get("keywords")),
        page.get("word_count", 0),
        page.get("crawled_at", datetime.now().isoformat()),
    ))
    page_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return page_id

def get_all_pages() -> list:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pages ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    pages = []
    for row in rows:
        p = dict(row)
        p["keywords"] = [k.strip() for k in (p.get("keywords") or "").split(",") if k.strip()]
        pages.append(p)
    return pages

def migrate_from_json(json_path: str = "pages_w2.json") -> int:
    import json as _json
    with open(json_path, "r", encoding="utf-8") as f:
        pages = _json.load(f)
    for p in pages:
        insert_page(p)
    return len(pages)

def log_search(query: str, results_count: int, user_id: str = None) -> int:
    pass

