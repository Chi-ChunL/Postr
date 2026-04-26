import os
from contextlib import contextmanager

import psycopg2
import psycopg2.extras

DATABASE_URL = os.environ["DATABASE_URL"]


@contextmanager
def _db():
    """Yield a RealDictCursor and auto-commit/close."""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


def initDB() -> None:
    """Create all tables if they don't exist. Call once at startup."""
    with _db() as cur:
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


#Posts 

def getAllPosts() -> list[dict]:
    with _db() as cur:
        cur.execute("SELECT id, title, author, content, created_at FROM posts ORDER BY id DESC")
        return [dict(row) for row in cur.fetchall()]


def getPostById(post_id: int) -> dict | None:
    with _db() as cur:
        cur.execute(
            "SELECT id, title, author, content, created_at FROM posts WHERE id = %s",
            (post_id,),
        )
        row = cur.fetchone()
        return dict(row) if row else None


def createPost(title: str, author: str, content: str, created_at: str) -> int:
    with _db() as cur:
        cur.execute(
            "INSERT INTO posts (title, author, content, created_at) VALUES (%s, %s, %s, %s) RETURNING id",
            (title, author, content, created_at),
        )
        return cur.fetchone()["id"]


def updatePost(post_id: int, title: str, author: str, content: str) -> bool:
    with _db() as cur:
        cur.execute(
            "UPDATE posts SET title = %s, author = %s, content = %s WHERE id = %s",
            (title, author, content, post_id),
        )
        return cur.rowcount > 0


def deletePost(post_id: int) -> bool:
    with _db() as cur:
        cur.execute("DELETE FROM posts WHERE id = %s", (post_id,))
        return cur.rowcount > 0


#Replies

def getReplies(post_id: int) -> list[dict]:
    with _db() as cur:
        cur.execute(
            "SELECT id, post_id, author, content, created_at FROM replies WHERE post_id = %s ORDER BY id ASC",
            (post_id,),
        )
        return [dict(row) for row in cur.fetchall()]


def createReply(post_id: int, author: str, content: str, created_at: str) -> int:
    with _db() as cur:
        cur.execute(
            "INSERT INTO replies (post_id, author, content, created_at) VALUES (%s, %s, %s, %s) RETURNING id",
            (post_id, author, content, created_at),
        )
        return cur.fetchone()["id"]