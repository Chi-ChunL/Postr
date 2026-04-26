import requests
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, ListView, ListItem, Label, Markdown, TextArea

from client.features import NewPostScreen, DeletePostScreen, EditPostScreen
from client.login import LoginScreen
from client.serverSelect import ServerSelectScreen
from server.auth import createUserTable


class PostrApp(App):
    CSS_PATH = "postr.tcss"
    BINDINGS = [
        Binding("escape", "escape_quit", "Back / Quit"),
        Binding("r", "reload_posts", "Reload Posts"),
        Binding("d", "delete_post", "Delete Post"),
        Binding("e", "edit_post", "Edit Post"),
        Binding("n", "new_post", "New Post"),
        Binding("c", "reply_post", "Reply"),
        Binding("ctrl+s", "submit_reply", "Send Reply"),
        Binding("ctrl+q", "noop", show=False),
    ]

    def __init__(self):
        super().__init__()
        self.onceEscape = False
        self.currentPost = None
        self.currentUser = None
        self.serverUrl = None

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

                with Vertical(id="replyPane"):
                    yield Label("REPLY", classes="viewerTitle")
                    yield TextArea("", id="replyTextArea")

        yield Footer()

    def on_mount(self) -> None:
        createUserTable()

        def handleServerResult(url: str | None) -> None:
            if not url:
                self.exit()
                return

            self.serverUrl = url
            self.notify(f"Connected to {self.serverUrl}", timeout=3)
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

        self.push_screen(ServerSelectScreen(), handleServerResult)

    def formatPostPreview(self, post: dict) -> str:
        return f"""# {post['title']}

**Author:** {post['author']}  
**Created:** {post['created_at']}

{post['content']}
"""

    def formatReplies(self, replies: list[dict]) -> str:
        if not replies:
            return "\n## Replies\n\nNo replies yet."

        reply_blocks = ["\n## Replies\n"]
        for reply in replies:
            reply_blocks.append(
                f"### {reply['author']} — {reply['created_at']}\n\n{reply['content']}\n"
            )
        return "\n".join(reply_blocks)

    def ensureServerSelected(self) -> bool:
        if not self.serverUrl:
            self.notify("No server selected.", timeout=3)
            return False
        return True

    def ensurePostSelected(self, action: str) -> bool:
        if self.currentPost is None:
            self.notify(f"No post selected to {action}", timeout=2)
            return False
        return True

    def isCurrentUserAuthor(self) -> bool:
        if self.currentPost is None or self.currentUser is None:
            return False
        return self.currentPost.get("author") == self.currentUser

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

    def validReplyContent(self, content: str) -> tuple[bool, str]:
        if content.strip() == "":
            return False, "Reply can't be empty."
        if len(content) > 5000:
            return False, "Reply must be at most 5000 characters."
        return True, ""

    def clearReplyBox(self) -> None:
        reply_box = self.query_one("#replyTextArea", TextArea)
        reply_box.text = ""

    def loadPosts(self) -> None:
        if not self.serverUrl:
            return

        post_list = self.query_one("#postList", ListView)
        post_list.clear()

        try:
            response = requests.get(f"{self.serverUrl}/posts", timeout=5)
            response.raise_for_status()
            posts = response.json()
        except requests.RequestException:
            self.notify("Failed to load posts from server", timeout=3)
            post_list.append(
                ListItem(Label("Failed to load posts from server", classes="postItem"))
            )
            return

        if not posts:
            post_list.append(
                ListItem(Label("No posts available. Press N to create one!", classes="postItem"))
            )
            return

        for post in posts:
            item = ListItem(Label(post["title"], classes="postItem"))
            item.postData = post
            post_list.append(item)

    def refreshCurrentPostWithReplies(self) -> None:
        if self.currentPost is None:
            return

        viewer = self.query_one("#viewer", Markdown)
        preview = self.formatPostPreview(self.currentPost)

        replies = []
        if self.serverUrl:
            try:
                response = requests.get(
                    f"{self.serverUrl}/posts/{self.currentPost['id']}/replies",
                    timeout=5,
                )
                response.raise_for_status()
                replies = response.json()
            except requests.RequestException:
                self.notify("Failed to load replies from server", timeout=3)

        viewer.update(preview + self.formatReplies(replies))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item = event.item
        if not hasattr(item, "postData"):
            return

        self.currentPost = item.postData
        self.clearReplyBox()
        self.refreshCurrentPostWithReplies()

    def createPost(self, title: str) -> None:
        title = title.strip()

        ok, message = self.validPostTitle(title)
        if not ok:
            self.notify(message, timeout=3)
            return

        if not self.currentUser:
            self.notify("You must be logged in to create a post.", timeout=3)
            return

        if not self.ensureServerSelected():
            return

        content = "Write your post content here..."

        try:
            response = requests.post(
                f"{self.serverUrl}/posts",
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
        self.clearReplyBox()

        viewer = self.query_one("#viewer", Markdown)
        viewer.update(self.formatPostPreview(created_post) + self.formatReplies([]))

        self.notify(f"Post '{title}' is created!", timeout=3)

    def deletePost(self) -> None:
        if not self.ensurePostSelected("be deleted"):
            return
        if not self.ensureServerSelected():
            return
        if not self.isCurrentUserAuthor():
            self.notify("You can only delete your own posts.", timeout=3)
            return

        deletedName = self.currentPost["title"]
        deletedId = self.currentPost["id"]

        def handleDeleteResult(confirmed: bool) -> None:
            if not confirmed:
                self.notify("Post deletion cancelled", timeout=2)
                return

            try:
                response = requests.delete(
                    f"{self.serverUrl}/posts/{deletedId}",
                    json={"request_user": self.currentUser},
                    timeout=5,
                )
                response.raise_for_status()
            except requests.RequestException:
                self.notify("Failed to delete post from server.", timeout=3)
                return

            self.currentPost = None
            self.loadPosts()
            self.clearReplyBox()

            view = self.query_one("#viewer", Markdown)
            view.update("# Welcome to Postr\n\nSelect a post from the left, or press **N** to create one.")

            self.notify(f"Post '{deletedName}' deleted!", timeout=3)

        self.push_screen(DeletePostScreen(deletedName), handleDeleteResult)

    def editPost(self) -> None:
        if not self.ensurePostSelected("edit"):
            return
        if not self.ensureServerSelected():
            return
        if not self.isCurrentUserAuthor():
            self.notify("You can only edit your own posts.", timeout=3)
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
                    f"{self.serverUrl}/posts/{postId}",
                    json={
                        "title": oldTitle,
                        "author": oldAuthor,
                        "content": newContent,
                        "request_user": self.currentUser,
                    },
                    timeout=5,
                )
                response.raise_for_status()
                updated_post = response.json()
            except requests.RequestException:
                self.notify("Failed to edit post on server.", timeout=3)
                return

            self.currentPost = {
                "id": updated_post["id"],
                "title": updated_post["title"],
                "author": updated_post["author"],
                "content": updated_post["content"],
                "created_at": self.currentPost.get("created_at", "Unknown"),
            }

            self.loadPosts()
            self.refreshCurrentPostWithReplies()
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

    def action_delete_post(self) -> None:
        self.deletePost()

    def action_reply_post(self) -> None:
        if not self.ensurePostSelected("reply to"):
            return
        reply_box = self.query_one("#replyTextArea", TextArea)
        reply_box.focus()

    def action_submit_reply(self) -> None:
        if not self.ensurePostSelected("reply to"):
            return
        if not self.ensureServerSelected():
            return
        if not self.currentUser:
            self.notify("Please login first", timeout=2)
            return

        reply_box = self.query_one("#replyTextArea", TextArea)
        new_reply = reply_box.text

        ok, message = self.validReplyContent(new_reply)
        if not ok:
            self.notify(message, timeout=3)
            return

        post_id = self.currentPost["id"]

        try:
            response = requests.post(
                f"{self.serverUrl}/posts/{post_id}/replies",
                json={
                    "author": self.currentUser,
                    "content": new_reply,
                },
                timeout=5,
            )
            response.raise_for_status()
        except requests.RequestException:
            self.notify("Failed to post reply.", timeout=3)
            return

        self.clearReplyBox()
        self.refreshCurrentPostWithReplies()
        self.notify("Reply posted!", timeout=3)

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

    def escapeReset(self) -> None:
        self.onceEscape = False

    def action_noop(self) -> None:
        pass


def main():
    app = PostrApp()
    app.run()


if __name__ == "__main__":
    main()