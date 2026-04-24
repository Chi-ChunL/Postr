import sqlite3
from pathlib import Path

DB_NAME = Path(__file__).resolve().parent.parent / "postr.db"


def connectDB():
    return sqlite3.connect(DB_NAME)


def createPostsTable() -> None:
    conn = connectDB()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

def createPost(title: str, author: str, content: str, created_at: str) -> int:
    conn = connectDB()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO posts (title, author, content, created_at)
        VALUES (?, ?, ?, ?)
    """, (title, author, content, created_at))

    conn.commit()
    post_id = cursor.lastrowid
    conn.close()

    return post_id

def deletePost(post_id: int) -> bool:
    conn = connectDB()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    conn.commit()

    deleted = cursor.rowcount > 0
    conn.close()

    return deleted

def getAllPosts():
    conn = connectDB()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, author, content, created_at
        FROM posts
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]