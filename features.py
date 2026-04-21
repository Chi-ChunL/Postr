from textual.app import ComposeResult
from textual.containers import Center, Middle, Vertical
from textual.screen import ModalScreen
from textual.widgets import Label, Input, TextArea


class NewPostScreen(ModalScreen[str | None]):
    def compose(self) -> ComposeResult:
        with Center():
            with Middle():
                with Vertical(id="newPostBox"):
                    yield Label("Create a new post", classes="popupTitle")
                    yield Input(placeholder="Enter your post title...", id="newPostInput")
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
                        f"Are you sure you want to delete '{self.postName}'?\nThis action cannot be undone.",
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
            yield Label(f"Editing: {self.postName}", classes="popupTitle")
            yield Label("Ctrl+S to save, Esc to cancel without saving", classes="popupHelp")
            yield TextArea(self.content, id="editPostTextArea")

    def on_mount(self) -> None:
        self.query_one("#editPostTextArea", TextArea).focus()

    def action_save_post(self) -> None:
        content = self.query_one("#editPostTextArea", TextArea).text
        self.dismiss(content)

    def action_cancel(self) -> None:
        self.dismiss(None)