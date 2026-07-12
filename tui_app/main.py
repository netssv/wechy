from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from tui_app.ui.dashboard import Dashboard

class WechyTUIApp(App):
    """A Terminal User Interface application for Wechy Web Techy Overview."""

    CSS = """
    Screen {
        background: $surface;
    }
    """
    
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("q", "quit", "Quit application")
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header(show_clock=True)
        yield Dashboard()
        yield Footer()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

if __name__ == "__main__":
    app = WechyTUIApp()
    app.run()
