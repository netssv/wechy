from textual.app import ComposeResult
from textual.containers import Grid
from textual.widgets import Static, Placeholder, Markdown
from textual.widget import Widget

DASHBOARD_MD = """
# Welcome to Wechy Web Techy Overview

Use the **terminal** to orchestrate and evaluate your web components. 

- This is a *completely new architecture*.
- No legacy monolith dependencies.
- Fast, responsive, keyboard-driven navigation.
"""

class Dashboard(Widget):
    """The main dashboard view for the TUI."""
    
    DEFAULT_CSS = """
    Dashboard {
        layout: grid;
        grid-size: 2 2;
        grid-columns: 1fr 2fr;
        grid-rows: 1fr 1fr;
        padding: 1;
        grid-gutter: 1;
    }
    
    #sidebar {
        row-span: 2;
        background: $panel;
        border: solid $accent;
        padding: 1;
    }
    
    #content-top {
        background: $panel;
        border: solid $accent;
        padding: 1;
    }
    
    #content-bottom {
        background: $panel;
        border: solid $accent;
        padding: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("Navigation Menu\n\n[1] Overview\n[2] System Status\n[3] Web Analytics\n[4] Settings", id="sidebar")
        yield Markdown(DASHBOARD_MD, id="content-top")
        yield Placeholder("System Metrics Visualization (Coming Soon)", id="content-bottom")
