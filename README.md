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

