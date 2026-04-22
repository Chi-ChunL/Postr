from flask import Flask, jsonify

app = Flask(__name__)


@app.get("/posts")
def get_posts():
    return jsonify([
        {
            "id": 1,
            "title": "Hello",
            "author": "Chi",
            "content": "First post"
        }
    ])


if __name__ == "__main__":
    app.run(debug=True)