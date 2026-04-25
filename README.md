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


# Postr-TUI

Postr-TUI is a terminal-based blog/forum client built with **Python** and **Textual**. It connects to a **Flask + SQLite** backend and lets users log in, create posts, edit posts, delete posts, and browse content from either a **public server**, a **private local server**, or a **custom server URL**.

The project started as a local markdown blog tool and has since been developed into a client/server posting app with user accounts, packaged distribution, and support for both shared and self-hosted use.

---

## Features

- Terminal user interface built with **Textual**
- User login and registration
- Password hashing with **bcrypt**
- Create, view, edit, and delete posts
- Flask backend with SQLite storage
- Public / private / custom server selection
- Packaged for installation as `postr-tui`
- Dark modern terminal theme
- Full-screen edit view

---

## Project Structure

```text
Postr/
├── client/
│   ├── __init__.py
│   ├── main.py
│   ├── features.py
│   ├── login.py
│   ├── serverSelect.py
│   └── postr.tcss
├── server/
│   ├── __init__.py
│   ├── server.py
│   ├── db.py
│   └── auth.py
├── pyproject.toml
├── README.md
└── .gitignore
How It Works

Postr-TUI uses a split architecture:

Client: the Textual TUI that users interact with
Server: a Flask backend that handles authentication and post storage
Database: SQLite database (postr.db) used by the server

The client no longer relies on local markdown files for post management. Instead, it communicates with the backend through API routes.

Current Functionality

The current version supports:

Loading posts from the server
Creating posts through the server
Editing posts through the server
Deleting posts through the server
Login and account registration
Choosing between:
public server
private local server
custom server URL
API Routes

The backend currently supports these post routes:

GET /posts
POST /posts
PUT /posts/<id>
DELETE /posts/<id>

Authentication is currently handled through the app’s login/register flow backed by SQLite and bcrypt.

Installation
Install from source

Clone the repository and install locally:

pip install -e .

Then run:

postr-tui

Or run the client directly:

python -m client.main
Running the Server

From the project root:

python -m server.server

The default private/local server URL is:

http://127.0.0.1:5000
Running the Client

From the project root:

python -m client.main

When the client opens, it will ask you to choose a server mode:

Public server
Private local server
Custom server URL

After selecting a server, you can log in or register and begin posting.

Packaging

The project is packaged as:

postr-tui

It has been successfully built and uploaded to TestPyPI.

Example local build commands
pip install build twine
python -m build
Example local editable install
pip install -e .
Tech Stack
Frontend: Textual
Backend: Flask
Database: SQLite
Authentication: bcrypt
Packaging: pyproject.toml / PyPI-style packaging
Notes
postr.db is a SQLite binary database file and should not be edited in a normal text editor.
Build artefacts such as dist/ and *.egg-info/ should not be committed.
Runtime database files should usually be ignored by Git.
The project is still in active development.
Recommended .gitignore

The following are ignored to keep the repo clean:

dist/
*.egg-info/
*.db
__pycache__/
virtual environment folders
editor/system junk files
Development Progress So Far

Major milestones completed so far include:

full-screen edit view fix
migration from local post handling to server-backed CRUD
client/server split
Flask backend setup
SQLite posts table
working CRUD routes
client now reads and writes to the backend
startup server selection flow
package setup and TestPyPI upload
Future Plans

Planned improvements include:

replies / comments
better forum-style discussion flow
author-based permissions
logout / switch account
hosted public server deployment
easier private self-hosting
real PyPI release
cleaner post preview formatting
Public vs Private Use

Postr is being designed so users can choose between:

Public Mode

Connect to a shared hosted Postr server and interact with other users.

Private Mode

Run a local or self-hosted Flask server and keep the blog/forum private.

Custom Mode

Connect to any compatible Postr server URL.

This is intended to let Postr work both as:

a public shared posting app
a private self-hosted personal/community server
License

Add your chosen license here.
