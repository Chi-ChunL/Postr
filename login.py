from textual.app import ComposeResult
from textual.containers import Center, Middle, Vertical
from textual.screen import ModalScreen
from textual.widgets import Label, Input

class LoginScreen(ModalScreen[str | None]):
    def compose(self) -> ComposeResult:
        with Center():
            with Middle():
                with Vertical(id="loginBox"):
                    yield Label("Login to Postr", classes="popupTitle")
                    yield Input(placeholder="Enter your username...", id="loginInput")
                    yield Label("Press Enter to continue.", classes="popupHelp")


    def on_mount(self) -> None:
        self.query_one("#loginInput", Input).focus()
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        username = event.value.strip()
        if username == "":
            self.dismiss(None)
            return
        self.dismiss(username)