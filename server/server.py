from datetime import datetime
from flask import Flask, jsonify, request
from server.db import (
    initDB,
    getAllPosts,
    createPost,
    deletePost,
    updatePost,
    getReplies,
    createReply,
    getPostById,
    deleteReply,
)
app = Flask(__name__)
initDB()

TIMESTAMP_FMT = "%Y-%m-%d %H:%M:%S"


#Helpers 

def _get_request_user(data: dict) -> str:
    return (
        str(data.get("request_user", "")).strip()
        or str(request.args.get("request_user", "")).strip()
        or str(request.headers.get("X-Postr-User", "")).strip()
    )


def _validate_post_fields(title: str, author: str, content: str) -> str | None:
    """Return an error message string, or None if all fields are valid."""
    if not title:
        return "Title cannot be empty"
    if not author:
        return "Author cannot be empty"
    if not content:
        return "Content cannot be empty"
    if len(title) > 80:
        return "Title must be at most 80 characters"
    if len(author) > 20:
        return "Author must be at most 20 characters"
    if len(content) > 20000:
        return "Content must be at most 20000 characters"
    return None


def _err(msg: str, status: int):
    return jsonify({"error": msg}), status


#Routes 

@app.get("/")
def home():
    return jsonify({
        "message": "Postr server is running",
        "routes": ["/posts", "/posts/<id>/replies"],
    })


@app.get("/posts")
def get_posts():
    return jsonify(getAllPosts())


@app.post("/posts")
def create_post():
    data = request.get_json(silent=True)
    if not data:
        return _err("Invalid JSON data", 400)

    title   = str(data.get("title",   "")).strip()
    author  = str(data.get("author",  "")).strip()
    content = str(data.get("content", "")).strip()

    if err := _validate_post_fields(title, author, content):
        return _err(err, 400)

    created_at = datetime.now().strftime(TIMESTAMP_FMT)
    post_id = createPost(title, author, content, created_at)

    return jsonify({
        "id": post_id, "title": title, "author": author,
        "content": content, "created_at": created_at,
    }), 201


@app.delete("/posts/<int:post_id>")
def delete_post(post_id: int):
    data = request.get_json(silent=True) or {}
    request_user = _get_request_user(data)

    if not request_user:
        return _err("Request user is required", 400)

    post = getPostById(post_id)
    if post is None:
        return _err("Post not found", 404)
    if post["author"] != request_user:
        return _err("You can only delete your own posts", 403)

    deletePost(post_id)
    return jsonify({"message": "Post deleted successfully", "id": post_id})

@app.delete("/posts/<int:reply_id>")
def delete_reply(reply_id: int):
    data = request.get_json(silent=True) or {}

    request_user = (
        str(data.get("request_user", "")).strip()
        or str(request.args.get("request_user", "")).strip()
        or str(request.headers.get("X-Postr-User", "")).strip()
    )

    reply = getReplies(reply_id)

    if reply is None:
        return jsonify({"error": "Reply not found"}), 404
    
    if request_user == "":
        return jsonify({"error": "Request user is required"}),400
    
    if reply["author"] != request_user:
        return jsonify({"error": "You can only delete your own replies"}), 403
    
    deleted = deleteReply(reply_id)

    if not deleted:
        return jsonify({"error": "Reply not found"}), 404
    
    return jsonify ({
        "message": "Reply deleted successfully",
        "id": reply_id,
    }), 200

@app.put("/posts/<int:post_id>")
def update_post(post_id: int):
    data = request.get_json(silent=True) or {}
    request_user = _get_request_user(data)

    if not request_user:
        return _err("Request user is required", 400)

    post = getPostById(post_id)
    if post is None:
        return _err("Post not found", 404)
    if post["author"] != request_user:
        return _err("You can only edit your own posts", 403)

    title   = str(data.get("title",   "")).strip()
    author  = str(data.get("author",  "")).strip()
    content = str(data.get("content", "")).strip()

    if err := _validate_post_fields(title, author, content):
        return _err(err, 400)

    updatePost(post_id, title, author, content)
    return jsonify({
        "id": post_id, "title": title, "author": author,
        "content": content, "created_at": post["created_at"],
    })


@app.get("/posts/<int:post_id>/replies")
def get_replies(post_id: int):
    return jsonify(getReplies(post_id))


@app.post("/posts/<int:post_id>/replies")
def create_reply(post_id: int):
    data = request.get_json(silent=True)
    if not data:
        return _err("No JSON data provided", 400)

    author  = str(data.get("author",  "")).strip()
    content = str(data.get("content", "")).strip()

    if not author:
        return _err("Author cannot be empty", 400)
    if not content:
        return _err("Content cannot be empty", 400)
    if len(author) > 20:
        return _err("Author must be at most 20 characters", 400)
    if len(content) > 5000:
        return _err("Reply must be at most 5000 characters", 400)

    created_at = datetime.now().strftime(TIMESTAMP_FMT)
    reply_id = createReply(post_id, author, content, created_at)

    return jsonify({
        "id": reply_id, "post_id": post_id, "author": author,
        "content": content, "created_at": created_at,
    }), 201


if __name__ == "__main__":
    app.run(debug=True)