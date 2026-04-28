# Postr-TUI

Postr-TUI is a terminal-based blog and forum client built with **Python**, **Textual**, **Flask**, and database support for both **PostgreSQL** and **SQLite**.

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