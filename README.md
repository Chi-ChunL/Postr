# Postr-TUI

Postr-TUI is a terminal-based blog and forum client built with Python and Textual, and database support for both PostgreSQL and SQLite.

It allows users to connect to a public hosted server, run their own private local server, or connect to a custom server URL. Users can register, log in, create posts, reply to posts, delete their own content, and use a remembered login system. 

---

## Features

- Terminal user interface built with **Textual**
- Public, private, and custom server modes
- User login and registration
- Remember-me system using local config and system keyring
- Create, view, edit, and delete posts
- Author-only post editing and deletion
- Create and view replies
- Selectable replies
- Author-only reply deletion
- Admin moderation support for deleting inappropriate posts/replies
- Public hosting support with Railway
- PostgreSQL support for hosted deployment
- SQLite fallback for private local hosting
- Packaged for installation from PyPI as `postr-tui`

---

## Installation

Install from PyPI:

```bash
pip install postr-tui
```
## Server Mode
When Postr-TUI starts, you can choose how to connect.

### Public Mode
In thsi mode you connect to a public server where people can post and reply to blogs etc.

### Private Mode
In this mode you connect to your own local server if you want to run one yourself, it will connect to:
```bash
http://127.0.0.1:5000
```
as a default.

### Custum Mode
Allows you to enter any compatible Postr server URL.

This is useful for self-hosting, testing, or connecting to a server hosted elsewhere.

## Running a Private Local Server
```bash
git clone https://github.com/Chi-ChunL/Postr.git
cd Postr
```
Install dependencies:
```bash
pip install -r requirements.txt
```
And then run the server:
```bash
python -m server.server
```
Then now you can run the client at another terminal or another device by doing:
```bash
python -m client.main
```
## Database Support
Postr supports two main database modes.

###PostgreSQL
if DATABASE_URL is set, Postr uses PostgreSQL

###SQLite
If DATABASE_URL is not set, Postr automatically falls back to SQLite.

This is intended for local private hosting.

The local database file is created as:
```bash
postr.db
```
## Project Structure
```bash
Postr/
├── client/
│   ├── __init__.py
│   ├── main.py
│   ├── features.py
│   ├── login.py
│   ├── serverSelect.py
│   ├── config.py
│   ├── credentials.py
│   └── postr.tcss
├── server/
│   ├── __init__.py
│   ├── server.py
│   ├── db.py
│   └── auth.py
├── .github/
│   └── workflows/
│       └── publish.yml
├── pyproject.toml
├── requirements.txt
├── README.md
└── .gitignore
```

## Main Controls
| Key        | Action                      |
| ---------- | --------------------------- |
| `N`        | Create a new post           |
| `E`        | Edit selected post, or reply|
| `D`        | Delete selected post        |
| `C`        | Show or hide reply composer |
| `Shift + Enter` | Submit reply                |
| `X`        | Delete selected reply       |
| `R`        | Reload posts                |
| `L`        | Log out / switch account    |
| `Esc`      | Back / quit                 |

## Login And Registration

Postr includes a login screen with seperate Login and Register tabs.

- Use the left and right arrow keys to switch between tabs.
- Press Enter in the username or password field to submit.
- Use the Remember Me option to save login details locally.
- Passwords are stored using the system keyring, not directly    inside the config file.

## Remember Me System

Postr stores non-sensitive settings in a local config file such as:

- last username
- last server URL
- remember-me preference

Passwords are stored seperately and all passwrods are hashed


## Current Status
Postr-TUI currently supports:

- hosted public server mode
- private local server mode
- custom server mode
- posting
- replies
- selectable reply deletion
- author-only edit/delete permissions
- admin moderation
- PyPI installation
- GitHub Actions publishing

## Security Notice
This is an App in development and there may be vulnerablility that is unknown to me, if you want to add something, open an issue or PR on my ([GitHub](https://github.com/Chi-ChunL/Postr))