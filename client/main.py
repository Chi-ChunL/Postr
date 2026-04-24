from pathlib import Path
from datetime import datetime
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, ListView, ListItem, Label, Markdown
import requests

from client.features import NewPostScreen, DeletePostScreen, EditPostScreen
from client.login import LoginScreen
from server.auth import createUserTable

POSTS_DIR = Path("posts")
SERVER_URL = "http://127.0.0.1:5000"


#Main
class PostrApp(App):
    CSS_PATH = "postr.tcss"
    BINDINGS = [
        Binding("escape", "escape_quit", "Back / Quit"),
        Binding("r", "reload_posts", "Reload Posts"),
        Binding("d", "delete_post", "Delete Post"),
        Binding("e", "edit_post", "Edit Post"),
        Binding("ctrl+q", "noop", show=False),
        Binding("n", "new_post", "New Post"),
    ]

    def __init__(self):
        super().__init__()
        self.onceEscape = False
        self.currentPost = None
        self.currentUser = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Horizontal(id="mainLayout"):
            with Vertical(id="sidebar"):
                yield Label("POSTS", classes="sidebarTitle")
                yield Label("Drafts and saved markdown files", classes="sidebarSubTitle")
                yield Label("Not logged in", id="currentUserLabel")
                yield ListView(id="postList")

            with Vertical(id="contentPane"):
                yield Label("PREVIEW", classes="viewerTitle")
                yield Markdown(
                    "# Welcome to Postr\n\nSelect a post from the left, or press **N** to create one.",
                    id="viewer",
                )

        yield Footer()

    #App lifecycle
    def on_mount(self) -> None:
        createUserTable()
        POSTS_DIR.mkdir(exist_ok=True)
        self.loadPosts()

        def handleLoginResult(username: str | None) -> None:
            if isinstance(username, str) and username.strip():
                self.currentUser = username.strip()

                userLabel = self.query_one("#currentUserLabel", Label)
                userLabel.update(f"Current user: {self.currentUser}")
                self.notify(f"Logged in as {self.currentUser}", timeout=3)
            else:
                self.exit()


        self.push_screen(LoginScreen(), handleLoginResult)

    # Load posts
    def loadPosts(self) -> None:
        post_list = self.query_one("#postList", ListView)
        post_list.clear()

        try:
            response = requests.get(f"{SERVER_URL}/posts", timeout=5)
            response.raise_for_status()
            posts = response.json()
        
        except requests.RequestException:
            self.notify("Failed to load posts from server", timeout=3)
            post_list.append(ListItem(Label("Failed to load posts from server", classes="postItem")))
            return

        if not posts:
            post_list.append(ListItem(Label("No posts available. Press N to create one!", classes="postItem")))
            return
        for post in posts:
            item  = ListItem(Label(post["title"], classes="postItem"))
            item.postData = post
            post_list.append(item)
    # View post
    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item = event.item
        if not hasattr(item, "postData"):
            return 

        post = item.postData
        self.currentPost = post

        
        content = f"""# {post['title']}
**Author:**: {post['author']}
**Created:**: {post['created_at']}

{post['content']}
"""

        viewer = self.query_one("#viewer", Markdown)
        viewer.update(content)
    
    def makeSlug(self, title: str) -> str: 
        safe = title.lower().strip().replace(" ", "-")
        safe = "".join(char for char in safe if char.isalnum() or char == "-")
        return safe or "untitled"

    def createPost(self, title: str) -> None:
        title = title.strip()

        ok, message = self.validPostTitle(title)
        if not ok:
            self.notify(message, timeout=3)
            return

        POSTS_DIR.mkdir(exist_ok=True)

        slug = self.makeSlug(title)
        file_path = POSTS_DIR / f"{slug}.md"

        count = 1
        while file_path.exists():
            file_path = POSTS_DIR / f"{slug}-{count}.md"
            count += 1

        content = f"""---
title: {title}
author: {self.currentUser}
date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
status: draft
---

Write your post content here...
"""
        try:
            file_path.write_text(content, encoding="utf-8")
        except Exception:
            self.notify("Failed to create the post file", timeout=3)
            return 
        
        self.loadPosts()
        self.currentPostPath = file_path

        viewer = self.query_one("#viewer", Markdown)
        viewer.update(content)

        self.notify(f"Post '{title}' is created!", timeout=3)

    def validPostTitle(self, title: str) -> tuple[bool, str]:
        title = title.strip()
        if title == "":
            return False, "Title can't be empty."
        if len(title) > 80:
            return False, "Title must be at most 80 characters."
        return True, ""
    
    def validPostContent(self, content: str) -> tuple[bool, str]:
        if content.strip() == "":
            return False, "Content can't be empty."
        if len(content) > 20000:
            return False, "Content must be at most 20000 characters."
        return True, ""

    def deletePost(self) -> None:
        if self.currentPostPath is None:
            self.notify("No post selected to be deleted", timeout=2)
            return

        if not self.currentPostPath.exists():
            self.notify("Selected post file no longer exists", timeout=2)
            self.currentPostPath = None
            self.loadPosts()
            return

        deletedName = self.currentPostPath.stem
        deletedPath = self.currentPostPath


        def handleDeleteResult(confirmed: bool) -> None:
            if not confirmed:
                self.notify("Post deletion cancelled", timeout=2)
                return

            if not deletedPath.exists():
                self.notify("Post file no longer exists", timeout=2)
                self.currentPostPath = None
                self.loadPosts()
                return

            try:
                deletedPath.unlink()
            except Exception:
                self.notify("Failed to delete the post file", timeout=3)
                return
            
            self.currentPostPath = None
            self.loadPosts()

            view = self.query_one("#viewer", Markdown)
            view.update("# Welcome to Postr\n\nSelect a post from the left, or press **N** to create one.")

            self.notify(f"Post '{deletedName}' deleted!", timeout=3)

        self.push_screen(DeletePostScreen(deletedName), handleDeleteResult)

    # Edit post
    def editPost(self) -> None:
        if self.currentPostPath is None:
            self.notify("No post selected to edit", timeout=2)
            return

        if not self.currentPostPath.exists():
            self.notify("Selected post file is not there anymore", timeout=2)
            self.currentPostPath = None
            self.loadPosts()
            return

        postPath = self.currentPostPath
        oldContent = postPath.read_text(encoding="utf-8")

        def handleEditResult(newContent: str | None) -> None:
            if newContent is None:
                self.notify("Edit cancelled", timeout=2)
                return
            
            ok, message = self.validPostContent(newContent)
            if not ok:
                self.notify(message, timeout=3)
                return
            

            try:
                postPath.write_text(newContent, encoding="utf-8")
            except Exception:
                self.notify("Failed to save the post file", timeout=3)
                return
            
            viewer = self.query_one("#viewer", Markdown)
            viewer.update(newContent)

            self.loadPosts()
            self.notify(f"Post '{postPath.stem}' saved!", timeout=3)

        self.push_screen(EditPostScreen(postPath.stem, oldContent), handleEditResult)

    def newPost(self) -> None:
        if self.currentUser is None:
            self.notify("Please log in first", timeout=2)
            return

        def handleResult(title: str | None) -> None:
            if not isinstance(title, str):
                return
            title = title.strip()
            ok, message = self.validPostTitle(title)
            if not ok:
                self.notify(message, timeout=3)
                return
            self.createPost(title)

        self.push_screen(NewPostScreen(), handleResult)

    def action_new_post(self) -> None:
        self.newPost()

    def action_edit_post(self) -> None:
        self.editPost()

    def reloadPosts(self) -> None:
        self.loadPosts()
        self.notify("Posts reloaded", timeout=2)

    def action_reload_posts(self) -> None:
        self.reloadPosts()

    def escapeQuit(self) -> None:
        if self.onceEscape:
            self.exit()
            return

        self.onceEscape = True
        self.notify("Press Esc again to quit", timeout=2)
        self.set_timer(2, self.escapeReset)

    def action_escape_quit(self) -> None:
        self.escapeQuit()

    def action_delete_post(self) -> None:
        self.deletePost()

    def escapeReset(self) -> None:
        self.onceEscape = False

    def action_noop(self) -> None:
        pass


if __name__ == "__main__":
    app = PostrApp()
    app.run()