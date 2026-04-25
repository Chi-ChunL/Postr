# Postr

Postr is a terminal-based blog/forum client built with Python and Textual. It connects to a Flask + SQLite backend and lets users log in, create posts, edit posts, delete posts, and browse content from either a public server or their own private one.

## Features

- Terminal user interface built with **Textual**
- User login and registration
- Create, edit, delete, and view posts
- Flask backend with SQLite storage
- Public / private / custom server selection
- Packaged for installation as `postr-tui`

## Project Structure

```text
Postr/
├── client/
│   ├── main.py
│   ├── features.py
│   ├── login.py
│   ├── serverSelect.py
│   └── postr.tcss
├── server/
│   ├── server.py
│   ├── db.py
│   └── auth.py
├── pyproject.toml
└── README.md