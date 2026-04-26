import requests
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, ListView, ListItem, Label, Markdown, TextArea
from textual.worker import Worker, get_current_worker

from client.features import NewPostScreen, DeletePostScreen, EditPostScreen
from client.login import LoginScreen
from client.serverSelect import ServerSelectScreen
from server.auth import createUserTable

WELCOME_MD = "# Welcome to Postr\n\nSelect a post from the left, or press **N** to create one."
TIMEOUT = 5

#Main application
class PostrApp(App):
    CSS_PATH = "postr.tcss"
    BINDINGS = [
        Binding("escape",  "escape_quit",    "Back / Quit"),
        Binding("r",       "reload_posts",   "Reload"),
        Binding("n",       "new_post",       "New Post"),
        Binding("e",       "edit_post",      "Edit Post"),
        Binding("d",       "delete_post",    "Delete Post"),
        Binding("c",       "reply_post",     "Reply"),
        Binding("ctrl+s",  "submit_reply",   "Send Reply"),
        Binding("ctrl+q",  "noop",           show=False),
    ]

    def __init__(self):
        super().__init__()
        self._escape_armed = False
        self.currentPost: dict | None = None
        self.currentUser: str | None = None
        self.serverUrl:   str | None = None

    #Layout 

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
                yield Markdown(WELCOME_MD, id="viewer")
                with Vertical(id="replyPane"):
                    yield Label("REPLY", classes="viewerTitle")
                    yield TextArea("", id="replyTextArea")
        yield Footer()

    # Startup

    def on_mount(self) -> None:
        createUserTable()

        def on_server(url: str | None) -> None:
            if not url:
                self.exit()
                return
            self.serverUrl = url
            self.notify(f"Connected to {url}", timeout=3)
            self.loadPosts()
            self.push_screen(LoginScreen(), on_login)

        def on_login(username: str | None) -> None:
            if not (isinstance(username, str) and username.strip()):
                self.exit()
                return
            self.currentUser = username.strip()
            self.query_one("#currentUserLabel", Label).update(f"Logged in as {self.currentUser}")
            self.notify(f"Welcome, {self.currentUser}!", timeout=3)

        self.push_screen(ServerSelectScreen(), on_server)

    #Formatting 

    def _formatPost(self, post: dict) -> str:
        return (
            f"# {post['title']}\n\n"
            f"**Author:** {post['author']}  \n"
            f"**Created:** {post['created_at']}\n\n"
            f"{post['content']}\n"
        )

    def _formatReplies(self, replies: list[dict]) -> str:
        if not replies:
            return "\n## Replies\n\nNo replies yet."
        blocks = ["\n## Replies\n"]
        for r in replies:
            blocks.append(f"### {r['author']} — {r['created_at']}\n\n{r['content']}\n")
        return "\n".join(blocks)

    #Validation 

    def _validate(self, value: str, kind: str) -> tuple[bool, str]:
        value = value.strip()
        limits = {"title": (80, "Title"), "content": (20000, "Post content"), "reply": (5000, "Reply")}
        label, max_len = limits[kind][1], limits[kind][0]
        if not value:
            return False, f"{label} can't be empty."
        if len(value) > max_len:
            return False, f"{label} must be at most {max_len} characters."
        return True, ""

    #Guards 

    def _requirePost(self, action: str) -> bool:
        if self.currentPost is None:
            self.notify(f"No post selected to {action}", timeout=2)
            return False
        return True

    def _requireServer(self) -> bool:
        if not self.serverUrl:
            self.notify("No server selected.", timeout=3)
            return False
        return True

    def _requireAuthor(self) -> bool:
        if not self.currentPost or not self.currentUser:
            return False
        if self.currentPost.get("author") != self.currentUser:
            self.notify("You can only do that to your own posts.", timeout=3)
            return False
        return True

    #Post list
    def loadPosts(self) -> None:
        self.run_worker(self._fetchAndRenderPosts(), exclusive=True)

    async def _fetchAndRenderPosts(self) -> None:
        worker = get_current_worker()
        post_list = self.query_one("#postList", ListView)
        try:
            response = await self.run_in_thread(
                lambda: requests.get(f"{self.serverUrl}/posts", timeout=TIMEOUT)
            )
            response.raise_for_status()
            posts = response.json()
        except requests.RequestException:
            if not worker.is_cancelled:
                self.notify("Failed to load posts from server", timeout=3)
            return
        if worker.is_cancelled:
            return
        post_list.clear()
        if not posts:
            post_list.append(ListItem(Label("No posts yet. Press N to create one!", classes="postItem")))
            return
        for post in posts:
            item = ListItem(Label(post["title"], classes="postItem"))
            item.postData = post
            post_list.append(item)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item = event.item
        if not hasattr(item, "postData"):
            return
        self.currentPost = item.postData
        self._clearReply()
        self.run_worker(self._fetchAndRenderViewer(), exclusive=True)

    async def _fetchAndRenderViewer(self) -> None:
        if self.currentPost is None:
            return
        worker = get_current_worker()
        post = self.currentPost
        try:
            response = await self.run_in_thread(
                lambda: requests.get(
                    f"{self.serverUrl}/posts/{post['id']}/replies", timeout=TIMEOUT
                )
            )
            response.raise_for_status()
            replies = response.json()
        except requests.RequestException:
            if not worker.is_cancelled:
                self.notify("Failed to load replies.", timeout=3)
            replies = []
        if not worker.is_cancelled:
            self.query_one("#viewer", Markdown).update(
                self._formatPost(post) + self._formatReplies(replies)
            )
    

    def _clearReply(self) -> None:
        self.query_one("#replyTextArea", TextArea).text = ""

    #Actions

    def action_new_post(self) -> None:
        if not self.currentUser:
            self.notify("Please log in first.", timeout=2)
            return

        def on_title(title: str | None) -> None:
            if not isinstance(title, str):
                return
            ok, msg = self._validate(title, "title")
            if not ok:
                self.notify(msg, timeout=3)
                return
            self.run_worker(self._createPost(title.strip()), exclusive=True)

        self.push_screen(NewPostScreen(), on_title)

    async def _createPost(self, title: str) -> None:
        worker = get_current_worker()
        try:
            response = await self.run_in_thread(
                lambda: requests.post(
                    f"{self.serverUrl}/posts",
                    json={"title": title, "author": self.currentUser, "content": "Write your post here..."},
                    timeout=TIMEOUT,
                )
            )
            response.raise_for_status()
            self.currentPost = response.json()
        except requests.RequestException:
            if not worker.is_cancelled:
                self.notify("Failed to create post.", timeout=3)
            return
        if worker.is_cancelled:
            return
        self.loadPosts()
        self._clearReply()
        await self._fetchAndRenderViewer()
        self.notify(f"Post '{title}' created!", timeout=3)
        
    def action_edit_post(self) -> None:
        if not self._requirePost("edit") or not self._requireServer() or not self._requireAuthor():
            return
        post_id = self.currentPost["id"]
        title   = self.currentPost["title"]
        author  = self.currentPost["author"]
        content = self.currentPost["content"]

        def on_edit(new_content: str | None) -> None:
            if new_content is None:
                self.notify("Edit cancelled.", timeout=2)
                return
            ok, msg = self._validate(new_content, "content")
            if not ok:
                self.notify(msg, timeout=3)
                return
            self.run_worker(self._updatePost(post_id, title, author, new_content), exclusive=True)

        self.push_screen(EditPostScreen(title, content), on_edit)

    async def _updatePost(self, post_id: int, title: str, author: str, content: str) -> None:
        worker = get_current_worker()
        created_at = self.currentPost.get("created_at", "Unknown")
        try:
            response = await self.run_in_thread(
                lambda: requests.put(
                    f"{self.serverUrl}/posts/{post_id}",
                    json={"title": title, "author": author, "content": content, "request_user": self.currentUser},
                    timeout=TIMEOUT,
                )
            )
            response.raise_for_status()
            updated = response.json()
        except requests.RequestException:
            if not worker.is_cancelled:
                self.notify("Failed to edit post.", timeout=3)
            return
        if worker.is_cancelled:
            return
        self.currentPost = {**updated, "created_at": created_at}
        self.loadPosts()
        await self._fetchAndRenderViewer()
        self.notify(f"Post '{title}' updated!", timeout=3)

    def action_delete_post(self) -> None:
        if not self._requirePost("delete") or not self._requireServer() or not self._requireAuthor():
            return
        title = self.currentPost["title"]
        post_id = self.currentPost["id"]

        def on_confirm(confirmed: bool) -> None:
            if not confirmed:
                self.notify("Deletion cancelled.", timeout=2)
                return
            self.run_worker(self._deletePost(post_id, title), exclusive=True)

        self.push_screen(DeletePostScreen(title), on_confirm)

    async def _deletePost(self, post_id: int, title: str) -> None:
        worker = get_current_worker()
        try:
            response = await self.run_in_thread(
                lambda: requests.delete(
                    f"{self.serverUrl}/posts/{post_id}",
                    json={"request_user": self.currentUser},
                    timeout=TIMEOUT,
                )
            )
            response.raise_for_status()
        except requests.RequestException:
            if not worker.is_cancelled:
                self.notify("Failed to delete post.", timeout=3)
            return
        if worker.is_cancelled:
            return
        self.currentPost = None
        self.loadPosts()
        self._clearReply()
        self.query_one("#viewer", Markdown).update(WELCOME_MD)
        self.notify(f"Post '{title}' deleted!", timeout=3)

    def action_reply_post(self) -> None:
        if not self._requirePost("reply to"):
            return
        self.query_one("#replyTextArea", TextArea).focus()

    def action_submit_reply(self) -> None:
        if not self._requirePost("reply to") or not self._requireServer():
            return
        if not self.currentUser:
            self.notify("Please log in first.", timeout=2)
            return
        content = self.query_one("#replyTextArea", TextArea).text
        ok, msg = self._validate(content, "reply")
        if not ok:
            self.notify(msg, timeout=3)
            return
        self.run_worker(self._submitReply(self.currentPost["id"], content), exclusive=True)

    async def _submitReply(self, post_id: int, content: str) -> None:
        worker = get_current_worker()
        try:
            response = await self.run_in_thread(
                lambda: requests.post(
                    f"{self.serverUrl}/posts/{post_id}/replies",
                    json={"author": self.currentUser, "content": content},
                    timeout=TIMEOUT,
                )
            )
            response.raise_for_status()
        except requests.RequestException:
            if not worker.is_cancelled:
                self.notify("Failed to post reply.", timeout=3)
            return
        if worker.is_cancelled:
            return
        self._clearReply()
        await self._fetchAndRenderViewer()
        self.notify("Reply posted!", timeout=3)

    def action_reload_posts(self) -> None:
        self.loadPosts()
        self.notify("Posts reloaded.", timeout=2)

    def action_escape_quit(self) -> None:
        if self._escape_armed:
            self.exit()
            return
        self._escape_armed = True
        self.notify("Press Esc again to quit.", timeout=2)
        self.set_timer(2, lambda: setattr(self, "_escape_armed", False))

    def action_noop(self) -> None:
        pass


def main():
    PostrApp().run()


if __name__ == "__main__":
    main()