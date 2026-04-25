import requests
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, ListView, ListItem, Label, Markdown

from client.features import NewPostScreen, DeletePostScreen, EditPostScreen
from client.login import LoginScreen
from server.auth import createUserTable

SERVER_URL = "http://127.0.0.1:5000"


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

    def on_mount(self) -> None:
        createUserTable()
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
            item = ListItem(Label(post["title"], classes="postItem"))
            item.postData = post
            post_list.append(item)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item = event.item
        if not hasattr(item, "postData"):
            return

        post = item.postData
        self.currentPost = post

        content = f"""# {post['title']}

**Author:** {post['author']}  
**Created:** {post['created_at']}

{post['content']}
"""

        viewer = self.query_one("#viewer", Markdown)
        viewer.update(content)

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

    def createPost(self, title: str) -> None:
        title = title.strip()

        ok, message = self.validPostTitle(title)
        if not ok:
            self.notify(message, timeout=3)
            return

        if not self.currentUser:
            self.notify("You must be logged in to create a post.", timeout=3)
            return

        content = "Write your post content here..."

        try:
            response = requests.post(
                f"{SERVER_URL}/posts",
                json={
                    "title": title,
                    "author": self.currentUser,
                    "content": content,
                },
                timeout=5,
            )
            response.raise_for_status()
            created_post = response.json()
        except requests.RequestException:
            self.notify("Failed to create post on server.", timeout=3)
            return

        self.loadPosts()
        self.currentPost = created_post

        preview = f"""# {created_post['title']}

**Author:** {created_post['author']}  
**Created:** {created_post['created_at']}

{created_post['content']}
"""

        viewer = self.query_one("#viewer", Markdown)
        viewer.update(preview)

        self.notify(f"Post '{title}' is created!", timeout=3)

    def deletePost(self) -> None:
        if self.currentPost is None:
            self.notify("No post selected to be deleted", timeout=2)
            return

        deletedName = self.currentPost["title"]
        deletedId = self.currentPost["id"]

        def handleDeleteResult(confirmed: bool) -> None:
            if not confirmed:
                self.notify("Post deletion cancelled", timeout=2)
                return

            try:
                response = requests.delete(f"{SERVER_URL}/posts/{deletedId}", timeout=5)
                response.raise_for_status()
            except requests.RequestException:
                self.notify("Failed to delete post from server.", timeout=3)
                return

            self.currentPost = None
            self.loadPosts()

            view = self.query_one("#viewer", Markdown)
            view.update("# Welcome to Postr\n\nSelect a post from the left, or press **N** to create one.")

            self.notify(f"Post '{deletedName}' deleted!", timeout=3)

        self.push_screen(DeletePostScreen(deletedName), handleDeleteResult)

    def editPost(self) -> None:
        if self.currentPost is None:
            self.notify("No post selected to edit", timeout=2)
            return

        postId = self.currentPost["id"]
        oldTitle = self.currentPost["title"]
        oldAuthor = self.currentPost["author"]
        oldContent = self.currentPost["content"]

        def handleEditResult(newContent: str | None) -> None:
            if newContent is None:
                self.notify("Edit cancelled", timeout=2)
                return

            ok, message = self.validPostContent(newContent)
            if not ok:
                self.notify(message, timeout=3)
                return

            try:
                response = requests.put(
                    f"{SERVER_URL}/posts/{postId}",
                    json={
                        "title": oldTitle,
                        "author": oldAuthor,
                        "content": newContent,
                    },
                    timeout=5,
                )
                response.raise_for_status()
                updated_post = response.json()
            except requests.RequestException:
                self.notify("Failed to save post to server.", timeout=3)
                return

            self.currentPost = {
                "id": updated_post["id"],
                "title": updated_post["title"],
                "author": updated_post["author"],
                "content": updated_post["content"],
                "created_at": self.currentPost.get("created_at", "Unknown"),
            }

            preview = f"""# {self.currentPost['title']}

**Author:** {self.currentPost['author']}  
**Created:** {self.currentPost['created_at']}

{self.currentPost['content']}
"""

            viewer = self.query_one("#viewer", Markdown)
            viewer.update(preview)

            self.loadPosts()
            self.notify(f"Post '{oldTitle}' updated!", timeout=3)

        self.push_screen(EditPostScreen(oldTitle, oldContent), handleEditResult)

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

def main():
    app = PostrApp()
    app.run()

if __name__ == "__main__":
    main()