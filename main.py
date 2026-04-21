from pathlib import Path
from datetime import datetime
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, Center, Middle
from textual.screen import ModalScreen
from textual.widgets import Header, Footer, ListView, ListItem, Label, Markdown, Input, TextArea

POSTS_DIR = Path("posts")

#New post screen box
class NewPostScreen(ModalScreen[str | None]):
    def compose(self) -> ComposeResult:
        with Center():
            with Middle():
                with Vertical(id="newPostBox"):
                    yield Label("Create a new post", classes="popupTitle")
                    yield Input(placeholder="Enter your Post Title...", id="newPostInput")
                    yield Label("Press Enter to create the post, or press Esc to cancel.", classes="popupHelp")

    def on_mount(self) -> None:
        self.query_one("#newPostInput", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        title = event.value.strip()
        if title == "":
            self.dismiss(None)
            return
        self.dismiss(title)

    def key_escape(self) -> None:
        self.dismiss(None)

# Delete post confirmation box
class DeletePostScreen(ModalScreen[bool]):
    def __init__(self, postName: str):
        super().__init__()
        self.postName = postName

    def compose(self) -> ComposeResult:
        with Center():
            with Middle():
                with Vertical(id="deletePostBox"):
                    yield Label("Delete Post", classes="popupTitle")
                    yield Label(
                        f"Are you sure you want to delete '{self.postName}'?\nYou will never see ts again.",
                        classes="popupHelp",
                    )
                    yield Label(
                        "Press Y or Enter to confirm. Press N or Esc to cancel.",
                        classes="popupHelp",
                    )

    def key_y(self) -> None:
        self.dismiss(True)

    def key_enter(self) -> None:
        self.dismiss(True)

    def key_n(self) -> None:
        self.dismiss(False)

    def key_escape(self) -> None:
        self.dismiss(False)

class EditPostScreen(ModalScreen[str | None]):
    BINDINGS = [
        ("ctrl+s", "save_post", "Save Post"),
        ("escape", "cancel", "Cancel Editing"),
    ]
    def __init__(self, postName: str, content: str):
        super().__init__()
        self.postName = postName
        self.content = content
    
    def compose(self) -> ComposeResult:
        with Vertical(id="editPostBox"):
            yield Label(f"Editiing: {self.postName}", classes="popupTitle")
            yield Label("Crtl+S to save, Esc to cancel without saving", classes="popupHelp")
            yield TextArea(self.content, id="editPostTextArea")
    
    def on_mount(self) -> None:
        self.query_one("#editPostTextArea", TextArea).focus()
    
    def action_save_post(self) -> None:
        content = self.query_one("#editPostTextArea", TextArea).text
        self.dismiss(content)
    
    def action_cancel(self) -> None:
        self.dismiss(None)
    
#Main app
class PostrApp(App):
    CSS_PATH = "postr.tcss"
    BINDINGS = [
        Binding("escape", "escape_quit", "Back / Quit"),
        Binding("r", "reload_posts", "Reload Posts"),
        Binding("d", "delete_post", "Delete Post"),
        Binding("ctrl+q", "noop", show=False),
        Binding("n", "new_post", "New Post"),
        Binding("e", "edit_post", "Edit Post"),
    ]

    def __init__(self):
        super().__init__()
        self.onceEscape = False
        self.currentPostPath = None

    #Compose UI
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Horizontal(id="mainLayout"):
            with Vertical(id="sidebar"):
                yield Label("POSTS", classes="sidebarTitle")
                yield Label("Drafts and saved markdown files", classes="sidebarSubTitle")
                yield ListView(id="postList")

            with Vertical(id="contentPane"):
                yield Label("PREVIEW", classes="viewerTitle")
                yield Markdown(
                    "# Welcome to Postr\n\nSelect a post from the left, or press **N** to create one.",
                    id="viewer",
                )

        yield Footer()

    #Ensure posts directory exists
    def on_mount(self) -> None:
        POSTS_DIR.mkdir(exist_ok=True)
        self.loadPosts()

    #load posts from disk
    def loadPosts(self) -> None:
        post_list = self.query_one("#postList", ListView)
        post_list.clear()

        files = sorted(POSTS_DIR.glob("*.md"))
        if not files:
            post_list.append(ListItem(Label("No posts yet bro")))
            return

        for file in files:
            item = ListItem(Label(file.stem))
            item.postPath = file
            post_list.append(item)

    #Handle past selected post and update viewer with new content
    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item = event.item
        if not hasattr(item, "postPath"):
            return

        path = item.postPath
        self.currentPostPath = path
        content = path.read_text(encoding="utf-8")
        viewer = self.query_one("#viewer", Markdown)
        viewer.update(content)

    #Slug....
    def makeSlug(self, title: str) -> str:
        safe = title.lower().strip().replace(" ", "-")
        safe = "".join(char for char in safe if char.isalnum() or char == "-")
        return safe or "untitled"

    #Create post logic
    def createPost(self, title: str) -> None:
        title = title.strip()
        if title == "":
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
date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
status: draft
---

Write your post content here...
"""

        file_path.write_text(content, encoding="utf-8")
        self.loadPosts()
        self.notify(f"Post '{title}' is created!", timeout=3)

    #Delete post logic
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

        #Handles resiult of delete confirmation
        def handleDeleteResult(confirmed: bool) -> None:
            if not confirmed:
                self.notify("Post deletion cancelled", timeout=2)
                return

            if not deletedPath.exists():
                self.notify("Post file no longer exists", timeout=2)
                self.currentPostPath = None
                self.loadPosts()
                return

            deletedPath.unlink()
            self.currentPostPath = None
            self.loadPosts()

            view = self.query_one("#viewer", Markdown)
            view.update("# Welcome to Postr\n\nSelect a post from the left, or press **N** to create one.")

            self.notify(f"Post '{deletedName}' deleted!", timeout=3)

        self.push_screen(DeletePostScreen(deletedName), handleDeleteResult)

    #New post logic
    def newPost(self) -> None:
        def handleResult(title: str | None) -> None:
            if isinstance(title, str) and title.strip():
                self.createPost(title)

        self.push_screen(NewPostScreen(), handleResult)

    #New post action
    def action_new_post(self) -> None:
        self.newPost()

    #Reload posts logic
    def reloadPosts(self) -> None:
        self.loadPosts()
        self.notify("Posts reloaded", timeout=2)

    #Reload posts
    def action_reload_posts(self) -> None:
        self.reloadPosts()

    # Escape to quit logic with confirmation
    def escapeQuit(self) -> None:
        if self.onceEscape:
            self.exit()
            return

        self.onceEscape = True
        self.notify("Press Esc again to quit", timeout=2)
        self.set_timer(2, self.escapeReset)

    # Escape key to quit
    def action_escape_quit(self) -> None:
        self.escapeQuit()

    #Delete post action
    def action_delete_post(self) -> None:
        self.deletePost()

    #Reset Escape
    def escapeReset(self) -> None:
        self.onceEscape = False

    #Prevent accidental Ctrl+Q quit because doesnt work in VS code terminal for some reason
    def action_noop(self) -> None:
        pass

    def editPost(self) -> None:
        if self.currentPostPath == None:
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
            if newContent == None:
                self.notify("Edit cancelled", timeout=2)
                return

            postPath.write_text(newContent, encoding="utf-8")

            viewer =  self.query_one("#viewer", Markdown)
            viewer.update(newContent)

            self.loadPosts()
            self.notify(f"Post '{postPath.stem}' saved!", timeout=3)    

        self.push_screen(EditPostScreen(postPath.stem, oldContent), handleEditResult)

    def action_edit_post(self) -> None:
        self.editPost()


if __name__ == "__main__":
    app = PostrApp()
    app.run()