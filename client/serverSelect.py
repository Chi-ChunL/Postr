from textual.app import ComposeResult
from textual.containers import Center, Middle, Vertical
from textual.screen import ModalScreen
from textual.widgets import Label, Input


class ServerSelectScreen(ModalScreen[str | None]):
    def compose(self) -> ComposeResult:
        with Center():
            with Middle():
                with Vertical(id="serverSelectBox"):
                    yield Label("Choose server mode", classes="popupTitle")
                    yield Label("1 = Public server", classes="popupHelp")
                    yield Label("2 = Private local server", classes="popupHelp")
                    yield Label("3 = Custom server URL", classes="popupHelp")
                    yield Input(placeholder="Enter 1, 2, or 3...", id="serverModeInput")
                    yield Label("", id="serverModeMessage", classes="popupHelp")

    def on_mount(self) -> None:
        self.query_one("#serverModeInput", Input).focus()

    def setMessage(self, text: str) -> None:
        self.query_one("#serverModeMessage", Label).update(text)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        choice = event.value.strip()

        if choice == "1":
            self.dismiss("https://your-public-postr-server.com")
            return

        if choice == "2":
            self.dismiss("http://127.0.0.1:5000")
            return

        if choice == "3":
            self.app.push_screen(CustomServerScreen(), self.handleCustomResult)
            return

        self.setMessage("Please enter 1, 2, or 3.")

    def handleCustomResult(self, url: str | None) -> None:
        if url:
            self.dismiss(url)

    def key_escape(self) -> None:
        self.dismiss(None)


class CustomServerScreen(ModalScreen[str | None]):
    def compose(self) -> ComposeResult:
        with Center():
            with Middle():
                with Vertical(id="serverSelectBox"):
                    yield Label("Custom server URL", classes="popupTitle")
                    yield Input(placeholder="Enter full URL...", id="customServerInput")
                    yield Label("Example: http://127.0.0.1:5000", classes="popupHelp")

    def on_mount(self) -> None:
        self.query_one("#customServerInput", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        url = event.value.strip()

        if url == "":
            self.dismiss(None)
            return

        self.dismiss(url)

    def key_escape(self) -> None:
        self.dismiss(None)