import os
import sqlite3
from pathlib import Path
from contextlib import contextmanager

DATABASE_URL = os.getenv("DATABASE_URL")
SQLITE_DB = Path(__file__).resolve().parent.parent / "postr.db"


if DATABASE_URL:
    import psycopg2
    import psycopg2.extras

    @contextmanager
    def _db():
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            yield conn, cur
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()
            conn.close()

    def initDB() -> None:
        with _db() as (_, cur):
            cur.execute("""
                CREATE TABLE IF NOT EXISTS posts (
                    id         SERIAL PRIMARY KEY,
                    title      TEXT NOT NULL,
                    author     TEXT NOT NULL,
                    content    TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS replies (
                    id         SERIAL PRIMARY KEY,
                    post_id    INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
                    author     TEXT NOT NULL,
                    content    TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)

    def getAllPosts() -> list[dict]:
        with _db() as (_, cur):
            cur.execute("SELECT id, title, author, content, created_at FROM posts ORDER BY id DESC")
            return [dict(row) for row in cur.fetchall()]

    def getPostById(post_id: int) -> dict | None:
        with _db() as (_, cur):
            cur.execute(
                "SELECT id, title, author, content, created_at FROM posts WHERE id = %s",
                (post_id,),
            )
            row = cur.fetchone()
            return dict(row) if row else None

    def createPost(title: str, author: str, content: str, created_at: str) -> int:
        with _db() as (_, cur):
            cur.execute(
                "INSERT INTO posts (title, author, content, created_at) VALUES (%s, %s, %s, %s) RETURNING id",
                (title, author, content, created_at),
            )
            return cur.fetchone()["id"]

    def updatePost(post_id: int, title: str, author: str, content: str) -> bool:
        with _db() as (_, cur):
            cur.execute(
                "UPDATE posts SET title = %s, author = %s, content = %s WHERE id = %s",
                (title, author, content, post_id),
            )
            return cur.rowcount > 0

    def deletePost(post_id: int) -> bool:
        with _db() as (_, cur):
            cur.execute("DELETE FROM posts WHERE id = %s", (post_id,))
            return cur.rowcount > 0

    def getReplies(post_id: int) -> list[dict]:
        with _db() as (_, cur):
            cur.execute(
                "SELECT id, post_id, author, content, created_at FROM replies WHERE post_id = %s ORDER BY id ASC",
                (post_id,),
            )
            return [dict(row) for row in cur.fetchall()]

    def getReplyById(reply_id: int) -> dict | None:
        with _db() as (_, cur):
            cur.execute(
                "SELECT id, post_id, author, content, created_at FROM replies WHERE id = %s",
                (reply_id,),
            )
            row = cur.fetchone()
            return dict(row) if row else None

    def createReply(post_id: int, author: str, content: str, created_at: str) -> int:
        with _db() as (_, cur):
            cur.execute(
                "INSERT INTO replies (post_id, author, content, created_at) VALUES (%s, %s, %s, %s) RETURNING id",
                (post_id, author, content, created_at),
            )
            return cur.fetchone()["id"]

    def deleteReply(reply_id: int) -> bool:
        with _db() as (_, cur):
            cur.execute("DELETE FROM replies WHERE id = %s", (reply_id,))
            return cur.rowcount > 0

    def updateReply(reply_id: int, content: str) -> bool:
        with _db() as (_, cur):
            cur.execute(
                "UPDATE replies SET content = %s WHERE id = %s",
                (content, reply_id),
            )
            return cur.rowcount > 0

else:
    @contextmanager
    def _db():
        conn = sqlite3.connect(SQLITE_DB)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        try:
            yield conn, cur
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()
            conn.close()

    def initDB() -> None:
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
                    post_id    INTEGER NOT NULL,
                    author     TEXT NOT NULL,
                    content    TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
                )
            """)


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


    def getReplies(post_id: int) -> list[dict]:
        with _db() as (_, cur):
            cur.execute(
                "SELECT id, post_id, author, content, created_at FROM replies WHERE post_id = ? ORDER BY id ASC",
                (post_id,),
            )
            return [dict(row) for row in cur.fetchall()]

    def getReplyById(reply_id: int) -> dict | None:
        with _db() as (_, cur):
            cur.execute(
                "SELECT id, post_id, author, content, created_at FROM replies WHERE id = ?",
                (reply_id,),
            )
            row = cur.fetchone()
            return dict(row) if row else None

    def createReply(post_id: int, author: str, content: str, created_at: str) -> int:
        with _db() as (_, cur):
            cur.execute(
                "INSERT INTO replies (post_id, author, content, created_at) VALUES (?, ?, ?, ?)",
                (post_id, author, content, created_at),
            )
            return cur.lastrowid

    def deleteReply(reply_id: int) -> bool:
        with _db() as (_, cur):
            cur.execute("DELETE FROM replies WHERE id = ?", (reply_id,))
            return cur.rowcount > 0
    
    def updateReply(reply_id: int, content: str) -> bool:
        with _db() as (_, cur):
            cur.execute(
                "UPDATE replies SET content = ? WHERE id = ?",
                (content, reply_id),
            )
            return cur.rowcount > 0