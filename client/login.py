from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Center, Middle, Vertical
from textual.screen import ModalScreen
from textual.widgets import Label, Input

from server.auth import registerUser, loginUser


class LoginScreen(ModalScreen[str | None]):
    BINDINGS = [
        Binding("enter", "login", "Log In"),
        Binding("ctrl+r", "register", "Register"),
        Binding("escape", "cancel_login", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        with Center():
            with Middle():
                with Vertical(id="loginBox"):
                    yield Label("Login to Postr", classes="popupTitle")
                    yield Label(
                        "Enter username and password. Press Enter to log in, or Ctrl+R to register.",
                        classes="popupHelp",
                    )
                    yield Input(placeholder="Username...", id="loginUsernameInput")
                    yield Input(placeholder="Password...", id="loginPasswordInput")
                    yield Label("", id="loginMessage", classes="popupHelp")

    def on_mount(self) -> None:
        self.query_one("#loginUsernameInput", Input).focus()

    def getUsername(self) -> str:
        return self.query_one("#loginUsernameInput", Input).value.strip()

    def getPassword(self) -> str:
        return self.query_one("#loginPasswordInput", Input).value

    def setMessage(self, text: str) -> None:
        self.query_one("#loginMessage", Label).update(text)

    def validUsername(self, username: str) -> tuple[bool, str]:
        if username == "":
            return False, "Username cannot be empty."
        if len(username) < 3:
            return False, "Username must be at least 3 characters."
        if len(username) > 20:
            return False, "Username must be at most 20 characters."
        if not username.replace("_", "").replace("-", "").isalnum():
            return False, "Username can only use letters, numbers, _ and -."
        return True, ""

    def validPassword(self, password: str) -> tuple[bool, str]:
        if password == "":
            return False, "Password cannot be empty."
        if len(password) < 6:
            return False, "Password must be at least 6 characters."
        if len(password) > 64:
            return False, "Password must be at most 64 characters."
        return True, ""

    def action_login(self) -> None:
        username = self.getUsername()
        password = self.getPassword()

        ok, message = self.validUsername(username)
        if not ok:
            self.setMessage(message)
            return

        ok, message = self.validPassword(password)
        if not ok:
            self.setMessage(message)
            return

        if loginUser(username, password):
            self.dismiss(username)
        else:
            self.setMessage("Invalid username or password.")

    def action_register(self) -> None:
        username = self.getUsername()
        password = self.getPassword()

        ok, message = self.validUsername(username)
        if not ok:
            self.setMessage(message)
            return

        ok, message = self.validPassword(password)
        if not ok:
            self.setMessage(message)
            return

        if registerUser(username, password):
            self.setMessage("Account created. Press Enter to log in.")
        else:
            self.setMessage("That username already exists.")

    def action_cancel_login(self) -> None:
        self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.action_login()