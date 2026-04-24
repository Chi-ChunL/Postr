from datetime import datetime
from flask import Flask, jsonify, request
from server.db import createPostsTable, getAllPosts, createPost

app = Flask(__name__)

createPostsTable()


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
        "created_at": created_at
    }), 201


if __name__ == "__main__":
    app.run(debug=True)