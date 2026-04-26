from datetime import datetime
from flask import Flask, jsonify, request
from server.db import (
    createPostsTable,
    getAllPosts,
    createPost,
    deletePost,
    updatePost,
    createRepliesTable,
    getReplies,
    createReply,
    getPostById,
)

app = Flask(__name__)

createPostsTable()
createRepliesTable()


@app.get("/")
def home():
    return jsonify({
        "message": "Postr server is running",
        "routes": [
            "/posts",
            "/posts/<id>/replies",
        ],
    })


@app.get("/posts")
def get_posts():
    return jsonify(getAllPosts())


@app.post("/posts")
def create_post():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400

    title = str(data.get("title", "")).strip()
    author = str(data.get("author", "")).strip()
    content = str(data.get("content", "")).strip()

    if title == "":
        return jsonify({"error": "Title cannot be empty"}), 400
    if author == "":
        return jsonify({"error": "Author cannot be empty"}), 400
    if content == "":
        return jsonify({"error": "Content cannot be empty"}), 400

    if len(title) > 80:
        return jsonify({"error": "Title must be at most 80 characters"}), 400
    if len(author) > 20:
        return jsonify({"error": "Author must be at most 20 characters"}), 400
    if len(content) > 20000:
        return jsonify({"error": "Content must be at most 20000 characters"}), 400

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    post_id = createPost(title, author, content, created_at)

    return jsonify({
        "message": "Post created successfully",
        "id": post_id,
        "title": title,
        "author": author,
        "content": content,
        "created_at": created_at,
    }), 201


@app.delete("/posts/<int:post_id>")
def deleted_post(post_id: int):

    data = request.get_json(silent=True) or {}
    request_user = str(data.get("request_user", "")).strip()

    post = getPostById(post_id)
    if post is None:
        return jsonify({"error": "Post not found"}), 404
    
    if request_user == "":
        return jsonify({"error": "Request user is required"}), 400
    
    if post["author"] != request_user:
        return jsonify({"error": "You can only delete your own post"}), 403

    deleted = deletePost(post_id)

    if not deleted:
        return jsonify({"error": "Post not found"}), 404

    return jsonify({
        "message": "Post deleted successfully",
        "id": post_id,
    }), 200


@app.put("/posts/<int:post_id>")
def update_post(post_id: int):
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400

    request_user = str(data.get("request_user", "")).strip()

    post = getPostById(post_id)
    if post is None:
        return jsonify({"error": "Post not found"}), 404

    if request_user == "":
        return jsonify({"error": "Request user is required"}), 400

    if post["author"] != request_user:
        return jsonify({"error": "You can only edit your own posts"}), 403

    title = str(data.get("title", "")).strip()
    author = str(data.get("author", "")).strip()
    content = str(data.get("content", "")).strip()

    if title == "":
        return jsonify({"error": "Title cannot be empty"}), 400
    if author == "":
        return jsonify({"error": "Author cannot be empty"}), 400
    if content == "":
        return jsonify({"error": "Content cannot be empty"}), 400

    if len(title) > 80:
        return jsonify({"error": "Title must be at most 80 characters"}), 400
    if len(author) > 20:
        return jsonify({"error": "Author must be at most 20 characters"}), 400
    if len(content) > 20000:
        return jsonify({"error": "Content must be at most 20000 characters"}), 400

    updated = updatePost(post_id, title, author, content)

    if not updated:
        return jsonify({"error": "Post not found"}), 404

    return jsonify({
        "message": "Post updated successfully",
        "id": post_id,
        "title": title,
        "author": author,
        "content": content
    }), 200


@app.get("/posts/<int:post_id>/replies")
def get_replies(post_id: int):
    return jsonify(getReplies(post_id))


@app.post("/posts/<int:post_id>/replies")
def create_reply(post_id: int):
    data = request.get_json()

    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    author = str(data.get("author", "")).strip()
    content = str(data.get("content", "")).strip()

    if author == "":
        return jsonify({"error": "Author cannot be empty"}), 400
    if content == "":
        return jsonify({"error": "Content cannot be empty"}), 400
    if len(author) > 20:
        return jsonify({"error": "Author must be 20 characters or fewer"}), 400
    if len(content) > 5000:
        return jsonify({"error": "Reply is too large"}), 400

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    reply_id = createReply(post_id, author, content, created_at)

    return jsonify({
        "id": reply_id,
        "post_id": post_id,
        "author": author,
        "content": content,
        "created_at": created_at,
    }), 201


if __name__ == "__main__":
    app.run(debug=True)