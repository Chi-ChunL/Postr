from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Center, Middle, Vertical, Horizontal
from textual.events import Key
from textual.screen import ModalScreen
from textual.widgets import Label, Input, Checkbox, Button

from server.auth import registerUser, loginUser


class LoginScreen(ModalScreen[dict | None]):
    BINDINGS = [
        Binding("left", "previous_tab", "Previous Tab", show=False),
        Binding("right", "next_tab", "Next Tab", show=False),
        Binding("escape", "cancel_login", "Cancel"),
    ]

    def __init__(self, remembered_username: str = "", remembered_password: str = ""):
        super().__init__()
        self.remembered_username = remembered_username
        self.remembered_password = remembered_password
        self.mode = "login"

    def compose(self) -> ComposeResult:
        with Center():
            with Middle():
                with Vertical(id="loginBox"):
                    yield Label("Postr Account", classes="popupTitle")

                    with Horizontal(id="authTabs"):
                        yield Button("Login", id="loginTab", classes="authTab activeTab")
                        yield Button("Register", id="registerTab", classes="authTab inactiveTab")

                    yield Label(
                        "Left/Right: switch tabs. Enter: submit.",
                        classes="popupHelp",
                    )

                    yield Input(
                        value=self.remembered_username,
                        placeholder="Username...",
                        id="loginUsernameInput",
                    )

                    yield Input(
                        value=self.remembered_password,
                        placeholder="Password...",
                        password=True,
                        id="loginPasswordInput",
                    )

                    yield Checkbox(
                        "Remember me",
                        value=bool(self.remembered_username),
                        id="rememberMeCheckbox",
                    )

                    yield Button("Log in", id="authButton")

                    yield Label("", id="loginMessage", classes="popupHelp")

    def on_mount(self) -> None:
        self.refreshTabs()

        if self.remembered_username:
            self.query_one("#loginPasswordInput", Input).focus()
        else:
            self.query_one("#loginUsernameInput", Input).focus()

    def refreshTabs(self) -> None:
        login_tab = self.query_one("#loginTab", Button)
        register_tab = self.query_one("#registerTab", Button)
        button = self.query_one("#authButton", Button)

        login_tab.remove_class("activeTab", "inactiveTab")
        register_tab.remove_class("activeTab", "inactiveTab")

        if self.mode == "login":
            login_tab.set_classes("activeTab")
            register_tab.set_classes("inactiveTab")
            button.label = "Log in"
        else:
            login_tab.set_classes("inactiveTab")
            register_tab.set_classes("activeTab")
            button.label = "Register"

        self.setMessage("")

    def action_next_tab(self) -> None:
        self.mode = "register" if self.mode == "login" else "login"
        self.refreshTabs()

    def action_previous_tab(self) -> None:
        self.mode = "register" if self.mode == "login" else "login"
        self.refreshTabs()

    def on_key(self, event: Key) -> None:
        focused = self.app.focused

        if event.key == "enter" and getattr(focused, "id", None) == "rememberMeCheckbox":
            checkbox = self.query_one("#rememberMeCheckbox", Checkbox)
            checkbox.value = not checkbox.value
            event.prevent_default()
            event.stop()

    def getUsername(self) -> str:
        return self.query_one("#loginUsernameInput", Input).value.strip()

    def getPassword(self) -> str:
        return self.query_one("#loginPasswordInput", Input).value

    def getRememberMe(self) -> bool:
        return self.query_one("#rememberMeCheckbox", Checkbox).value

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

    def submitCurrentMode(self) -> None:
        if self.mode == "login":
            self.action_login()
        else:
            self.action_register()

    def action_login(self) -> None:
        username = self.getUsername()
        password = self.getPassword()
        remember_me = self.getRememberMe()

        ok, message = self.validUsername(username)
        if not ok:
            self.setMessage(message)
            return

        ok, message = self.validPassword(password)
        if not ok:
            self.setMessage(message)
            return

        if loginUser(username, password):
            self.dismiss({
                "username": username,
                "password": password,
                "remember_me": remember_me,
            })
        else:
            self.setMessage("Invalid username or password.")

    def action_register(self) -> None:
        username = self.getUsername()
        password = self.getPassword()
        remember_me = self.getRememberMe()

        ok, message = self.validUsername(username)
        if not ok:
            self.setMessage(message)
            return

        ok, message = self.validPassword(password)
        if not ok:
            self.setMessage(message)
            return

        if not registerUser(username, password):
            self.setMessage("That username already exists.")
            return

        self.dismiss({
            "username": username,
            "password": password,
            "remember_me": remember_me,
        })

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "loginTab":
            self.mode = "login"
            self.refreshTabs()
            return

        if event.button.id == "registerTab":
            self.mode = "register"
            self.refreshTabs()
            return

        if event.button.id == "authButton":
            self.submitCurrentMode()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.submitCurrentMode()

    def action_cancel_login(self) -> None:
        self.dismiss(None)