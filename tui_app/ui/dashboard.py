import asyncio
import subprocess
from textual import work
from textual.app import ComposeResult
from textual.containers import Grid, Horizontal, Vertical
from textual.widgets import OptionList, Label, Input, Button, RichLog, Checkbox, RadioSet, RadioButton
from textual.widget import Widget

class Dashboard(Widget):
    """The main dashboard view for the TUI."""
    
    DEFAULT_CSS = """
    Dashboard {
        layout: grid;
        grid-size: 2 2;
        grid-columns: 1fr 3fr;
        grid-rows: auto 1fr;
        padding: 1;
        grid-gutter: 1;
    }
    
    #sidebar {
        row-span: 2;
        background: $panel;
        border: solid $accent;
        padding: 1;
    }
    
    #input-area {
        height: auto;
        background: $panel;
        border: solid $accent;
        padding: 1;
        layout: vertical;
    }

    #controls {
        height: auto;
        margin-top: 1;
        align: left middle;
    }
    
    #options-container {
        height: auto;
        margin-top: 1;
    }

    Button {
        margin-right: 1;
    }
    
    Checkbox {
        margin-right: 1;
    }
    
    RadioSet {
        layout: horizontal;
        background: $surface;
        border: none;
    }
    
    #output-log {
        background: $panel;
        border: solid $accent;
        padding: 1;
        height: 100%;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="sidebar"):
            yield Label("Navigation Menu", classes="menu-title")
            yield OptionList(
                "Overview",
                "DNS Tools",
                "Web Analytics",
                "Security Info",
                "Settings",
                id="nav-menu"
            )
            yield Label("\nStatus: Ready", id="status-label")
        
        with Vertical(id="input-area"):
            yield Input(placeholder="Enter a domain and press Enter (e.g. google.com)", id="url-input")
            
            with Horizontal(id="options-container"):
                yield Checkbox("Use +short in Dig", id="chk-short", value=True)
                with RadioSet(id="mode-radioset"):
                    yield RadioButton("Raw Data", id="radio-raw", value=True)
                    yield RadioButton("Insights", id="radio-insights")

            with Horizontal(id="controls"):
                yield Button("Run Dig (DNS)", id="btn-dig", variant="primary")
                yield Button("Run Curl (HTTP)", id="btn-curl", variant="success")
                yield Button("Run OpenSSL (Certs)", id="btn-openssl", variant="warning")
                
        yield RichLog(id="output-log", highlight=True, markup=False)

    def on_mount(self) -> None:
        self.output = self.query_one("#output-log", RichLog)
        self.url_input = self.query_one("#url-input", Input)
        self.chk_short = self.query_one("#chk-short", Checkbox)
        self.radio_insights = self.query_one("#radio-insights", RadioButton)
        self.output.write("TUI System Initialized. Enter a domain and press Enter to scan automatically...")

    @work(exclusive=False, thread=True)
    def run_system_command(self, cmd: str, title: str, parser_type: str) -> None:
        """Run a system command and stream or parse the output to the log."""
        insights_mode = self.radio_insights.value
        
        if not insights_mode:
            self.app.call_from_thread(self.output.write, f"\n$ {cmd}")
            
        try:
            process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            if not insights_mode:
                # Raw Data Mode: stream output directly
                for line in process.stdout:
                    self.app.call_from_thread(self.output.write, line.rstrip())
            else:
                # Insights Mode: capture output and parse it
                stdout_data, _ = process.communicate()
                self.parse_and_display_insights(title, stdout_data, parser_type)
                
            process.wait()
            
        except Exception as e:
            self.app.call_from_thread(self.output.write, f"Error executing {cmd}: {e}")

    def parse_and_display_insights(self, title: str, raw_data: str, parser_type: str) -> None:
        """Parse raw output into a polished insights format."""
        self.app.call_from_thread(self.output.write, f"\n--- {title} Insights ---")
        
        if not raw_data.strip():
            self.app.call_from_thread(self.output.write, "No data found or command failed.")
            return

        lines = raw_data.strip().split("\n")
        
        if parser_type == "dig":
            for line in lines:
                parts = line.split()
                if len(parts) >= 2 and parts[0].isdigit():
                    priority, server = parts[0], parts[1]
                    self.app.call_from_thread(self.output.write, f" -> Mail Server: {server} (Priority: {priority})")
                else:
                    self.app.call_from_thread(self.output.write, f" -> Record: {line}")
                    
        elif parser_type == "curl":
            server_info = "Unknown"
            status_code = "Unknown"
            for line in lines:
                if line.upper().startswith("HTTP/"):
                    status_code = line.strip()
                elif line.lower().startswith("server:"):
                    server_info = line.split(":", 1)[1].strip()
            self.app.call_from_thread(self.output.write, f" -> Status: {status_code}")
            self.app.call_from_thread(self.output.write, f" -> Server Tech: {server_info}")

        elif parser_type == "openssl":
            issuer = "Unknown"
            start_date = "Unknown"
            end_date = "Unknown"
            
            for line in lines:
                if line.startswith("issuer="):
                    issuer = line.replace("issuer=", "").strip()
                elif line.startswith("notBefore="):
                    start_date = line.replace("notBefore=", "").strip()
                elif line.startswith("notAfter="):
                    end_date = line.replace("notAfter=", "").strip()
                    
            self.app.call_from_thread(self.output.write, f" -> Certificate Issuer: {issuer}")
            self.app.call_from_thread(self.output.write, f" -> Valid From: {start_date}")
            self.app.call_from_thread(self.output.write, f" -> Valid Until: {end_date}")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Automatically scan when the user presses Enter in the Input field."""
        self.run_full_scan()

    def run_full_scan(self) -> None:
        url = self.url_input.value.strip()
        if not url:
            self.output.write("Please enter a URL first.")
            return
            
        domain = url.replace("https://", "").replace("http://", "").split("/")[0]
        short_flag = " +short" if self.chk_short.value else ""
        
        self.output.clear()
        self.output.write(f"Initiating automatic scan for {domain}...\n")
        
        self.run_system_command(f"dig mx {domain}{short_flag}", "DNS MX Records", "dig")
        self.run_system_command(f"curl -s -I https://{domain}", "HTTP Headers", "curl")
        self.run_system_command(f"echo | openssl s_client -connect {domain}:443 2>/dev/null | openssl x509 -noout -dates -subject -issuer", "SSL Certificate", "openssl")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        url = self.url_input.value.strip()
        
        if not url:
            self.output.write("Please enter a URL first.")
            return
            
        domain = url.replace("https://", "").replace("http://", "").split("/")[0]
        short_flag = " +short" if self.chk_short.value else ""

        if event.button.id == "btn-dig":
            self.run_system_command(f"dig mx {domain}{short_flag}", "DNS MX Records", "dig")
        elif event.button.id == "btn-curl":
            self.run_system_command(f"curl -s -I https://{domain}", "HTTP Headers", "curl")
        elif event.button.id == "btn-openssl":
            self.run_system_command(f"echo | openssl s_client -connect {domain}:443 2>/dev/null | openssl x509 -noout -dates -subject -issuer", "SSL Certificate", "openssl")

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Handle navigation menu selection."""
        menu_item = str(event.option.prompt)
        self.output.write(f"\n--- Navigated to: {menu_item} ---")
        if menu_item == "DNS Tools":
            self.output.write("Hint: Enter a domain and click 'Run Dig (DNS)'.")
        elif menu_item == "Web Analytics":
            self.output.write("Hint: Enter a domain and click 'Run Curl (HTTP)'.")
        elif menu_item == "Security Info":
            self.output.write("Hint: Enter a domain and click 'Run OpenSSL (Certs)'.")
        else:
            self.output.write("This module is currently under construction in the new TUI.")
