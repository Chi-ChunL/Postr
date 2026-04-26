import sqlite3
from contextlib import contextmanager
from pathlib import Path

_VOLUME = Path("/data")
DB_PATH = (_VOLUME / "postr.db") if _VOLUME.exists() else (Path(__file__).resolve().parent.parent / "postr.db")

#Check
@contextmanager
def _db():
    """Context manager that yields a Row-aware cursor and auto-commits/closes."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn, conn.cursor()
        conn.commit()
    finally:
        conn.close()


def initDB() -> None:
    """Create all tables if they don't exist. Call once at startup."""
    with _db() as (_, cur):
        cur.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                title      TEXT NOT NULL,
                author     TEXT NOT NULL,
                content    TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS replies (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id    INTEGER NOT NULL REFERENCES posts(id),
                author     TEXT NOT NULL,
                content    TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)


#Posts 
def getAllPosts() -> list[dict]:
    with _db() as (_, cur):
        cur.execute("SELECT id, title, author, content, created_at FROM posts ORDER BY id DESC")
        return [dict(row) for row in cur.fetchall()]


def getPostById(post_id: int) -> dict | None:
    with _db() as (_, cur):
        cur.execute(
            "SELECT id, title, author, content, created_at FROM posts WHERE id = ?",
            (post_id,),
        )
        row = cur.fetchone()
        return dict(row) if row else None


def createPost(title: str, author: str, content: str, created_at: str) -> int:
    with _db() as (_, cur):
        cur.execute(
            "INSERT INTO posts (title, author, content, created_at) VALUES (?, ?, ?, ?)",
            (title, author, content, created_at),
        )
        return cur.lastrowid

#Update
def updatePost(post_id: int, title: str, author: str, content: str) -> bool:
    with _db() as (_, cur):
        cur.execute(
            "UPDATE posts SET title = ?, author = ?, content = ? WHERE id = ?",
            (title, author, content, post_id),
        )
        return cur.rowcount > 0


def deletePost(post_id: int) -> bool:
    with _db() as (_, cur):
        cur.execute("DELETE FROM posts WHERE id = ?", (post_id,))
        return cur.rowcount > 0


#Replies
def getReplies(post_id: int) -> list[dict]:
    with _db() as (_, cur):
        cur.execute(
            "SELECT id, post_id, author, content, created_at FROM replies WHERE post_id = ? ORDER BY id ASC",
            (post_id,),
        )
        return [dict(row) for row in cur.fetchall()]


def createReply(post_id: int, author: str, content: str, created_at: str) -> int:
    with _db() as (_, cur):
        cur.execute(
            "INSERT INTO replies (post_id, author, content, created_at) VALUES (?, ?, ?, ?)",
            (post_id, author, content, created_at),
        )
        return cur.lastrowid