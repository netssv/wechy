#!/usr/bin/env python3
"""
wechy — Interactive TUI for Web Diagnostics & Audit.

Powered by Textual. Provides a beautiful main menu with access to:
  • Full AI-Agentic Audit (all skills orchestrated by LLM)
  • DNS Lookup (dig / nslookup wrappers)
  • SSL/TLS Inspector (openssl wrapper)
  • HTTP Probe (curl wrapper)
  • Security Headers Scan
  • Email Domain Validator (MX + SPF/DKIM/DMARC)
  • WHOIS Lookup
"""

import os
import re
import shutil
import subprocess
import sys
import time
from urllib.parse import urlparse

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, Center
from textual.screen import ModalScreen
from textual.widgets import (
    Header,
    Footer,
    Input,
    Button,
    Static,
    Label,
    ListView,
    ListItem,
    TabbedContent,
    TabPane,
    Log,
    RichLog,
    OptionList,
)
from textual.widgets.option_list import Option

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import AuditConfig
from models.audit_result import AuditReport
from skills.skill_registry import SkillRegistry

# Import skills to trigger auto-registration
import skills.dns_skill
import skills.ssl_skill
import skills.performance_skill
import skills.security_skill
import skills.whois_skill
import skills.tech_detection_skill


# ═══════════════════════════════════════════════════════════════════
# Helper: run a native Linux command and capture output
# ═══════════════════════════════════════════════════════════════════

def _run_native(cmd: list[str], timeout: int = 30) -> str:
    """Run a system command and return its combined stdout+stderr."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = result.stdout
        if result.stderr:
            output += "\n" + result.stderr
        return output.strip() or "(no output)"
    except FileNotFoundError:
        return f"[bold red]Command not found:[/] {cmd[0]}. Install it first."
    except subprocess.TimeoutExpired:
        return f"[bold red]Command timed out after {timeout}s.[/]"
    except Exception as e:
        return f"[bold red]Error:[/] {e}"


def _tool_available(name: str) -> bool:
    """Check if a CLI tool is installed."""
    return shutil.which(name) is not None


# ═══════════════════════════════════════════════════════════════════
# Main TUI Application
# ═══════════════════════════════════════════════════════════════════

class WechyApp(App):
    """wechy — Terminal User Interface for Web Diagnostics."""

    CSS = """
    Screen {
        background: #11111b;
    }

    /* ── Banner ─────────────────────────────────── */
    #banner {
        width: 100%;
        height: 5;
        content-align: center middle;
        background: #1e1e2e;
        color: #cdd6f4;
        border-bottom: heavy #4F46E5;
    }

    /* ── Main menu ──────────────────────────────── */
    #menu-container {
        width: 100%;
        height: 1fr;
        align: center middle;
    }

    OptionList {
        width: 72;
        height: auto;
        max-height: 20;
        background: #1e1e2e;
        border: round #4F46E5;
        padding: 1 2;
    }

    OptionList > .option-list--option-highlighted {
        background: #4F46E5;
        color: #ffffff;
    }

    /* ── Input bar (shown after menu selection) ── */
    #input-bar {
        dock: top;
        height: 4;
        background: #1e1e2e;
        border-bottom: solid #4F46E5;
        padding: 0 1;
    }

    #domain-input {
        width: 1fr;
    }

    #run-btn {
        width: 18;
        background: #4F46E5;
        color: white;
    }

    #run-btn:hover {
        background: #7C3AED;
    }

    #back-btn {
        width: 10;
        background: #313244;
        color: #cdd6f4;
    }

    /* ── Output area ────────────────────────────── */
    #output-area {
        width: 100%;
        height: 1fr;
        background: #181825;
        border: round #313244;
        margin: 1;
        padding: 1;
    }

    /* ── Tool indicators ────────────────────────── */
    #tool-label {
        dock: top;
        height: 1;
        background: #4F46E5;
        color: white;
        text-align: center;
    }

    /* ── Status bar  ────────────────────────────── */
    #status-label {
        dock: bottom;
        height: 1;
        background: #1e1e2e;
        color: #6c7086;
        text-align: center;
    }
    """

    TITLE = "wechy"
    SUB_TITLE = "Web Diagnostics & Audit TUI"
    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("escape", "go_back", "Back", show=True),
    ]

    # Menu items — each tuple: (label, internal_id)
    MENU_ITEMS = [
        ("🤖  AI Full Audit — Run all skills with AI analysis",          "ai_audit"),
        ("🌐  DNS Lookup — dig / nslookup queries",                      "dns_lookup"),
        ("🔒  SSL/TLS Inspector — openssl certificate details",          "ssl_inspect"),
        ("📡  HTTP Probe — curl response and headers",                   "http_probe"),
        ("🛡️  Security Headers Scan — check HSTS, CSP, etc.",           "sec_scan"),
        ("📧  Email Domain Validator — MX, SPF, DKIM, DMARC",           "email_check"),
        ("📄  WHOIS Lookup — domain registration info",                  "whois_lookup"),
        ("🔧  Tech Detection — server and framework fingerprint",        "tech_detect"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._current_tool: str | None = None

    # ── Compose: main menu ───────────────────────────────────────

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(
            "[bold #7c3aed]╔══════════════════════════════════════════════╗[/]\n"
            "[bold #7c3aed]║[/]  [bold white]wechy[/] [dim]— Web Check Your Site[/]              [bold #7c3aed]║[/]\n"
            "[bold #7c3aed]║[/]  [dim]Powered by AI-Agentic Skills & Linux CLI[/]  [bold #7c3aed]║[/]\n"
            "[bold #7c3aed]╚══════════════════════════════════════════════╝[/]",
            id="banner",
        )
        with Container(id="menu-container"):
            yield OptionList(
                *[Option(label, id=item_id) for label, item_id in self.MENU_ITEMS],
                id="main-menu",
            )
        yield Footer()

    # ── Menu selection ───────────────────────────────────────────

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        selected_id = event.option.id
        self._current_tool = selected_id
        self.push_screen(ToolScreen(selected_id))

    # ── Back action ──────────────────────────────────────────────

    def action_go_back(self) -> None:
        if len(self.screen_stack) > 1:
            self.pop_screen()


# ═══════════════════════════════════════════════════════════════════
# Tool Screen — shows input bar + output for any selected tool
# ═══════════════════════════════════════════════════════════════════

_TOOL_LABELS = {
    "ai_audit":     "🤖 AI Full Audit",
    "dns_lookup":   "🌐 DNS Lookup (dig / nslookup)",
    "ssl_inspect":  "🔒 SSL/TLS Inspector (openssl)",
    "http_probe":   "📡 HTTP Probe (curl)",
    "sec_scan":     "🛡️  Security Headers Scan",
    "email_check":  "📧 Email Domain Validator",
    "whois_lookup": "📄 WHOIS Lookup",
    "tech_detect":  "🔧 Tech Detection",
}

_INPUT_PLACEHOLDERS = {
    "ai_audit":     "Enter domain to audit (e.g. google.com)",
    "dns_lookup":   "Enter domain (e.g. example.com)",
    "ssl_inspect":  "Enter domain (e.g. github.com)",
    "http_probe":   "Enter full URL (e.g. https://example.com)",
    "sec_scan":     "Enter URL (e.g. https://example.com)",
    "email_check":  "Enter email domain (e.g. gmail.com)",
    "whois_lookup": "Enter domain (e.g. example.com)",
    "tech_detect":  "Enter URL (e.g. https://example.com)",
}


class ToolScreen(ModalScreen):
    """Full-screen view for a single diagnostic tool."""

    BINDINGS = [Binding("escape", "dismiss_screen", "Back to menu")]

    def __init__(self, tool_id: str) -> None:
        super().__init__()
        self.tool_id = tool_id

    def compose(self) -> ComposeResult:
        yield Static(_TOOL_LABELS.get(self.tool_id, self.tool_id), id="tool-label")
        with Horizontal(id="input-bar"):
            yield Input(
                placeholder=_INPUT_PLACEHOLDERS.get(self.tool_id, "Enter target..."),
                id="domain-input",
            )
            yield Button("Run", id="run-btn")
            yield Button("← Back", id="back-btn")
        yield RichLog(id="output-area", wrap=True, highlight=True, markup=True)
        yield Static("Ready. Enter a target and press Run.", id="status-label")

    # ── Button handlers ──────────────────────────────────────────

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back-btn":
            self.dismiss()
        elif event.button.id == "run-btn":
            self._execute()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self._execute()

    def action_dismiss_screen(self) -> None:
        self.dismiss()

    # ── Execution dispatcher ─────────────────────────────────────

    def _execute(self) -> None:
        target = self.query_one("#domain-input", Input).value.strip()
        if not target:
            self.query_one("#output-area", RichLog).write("[bold red]Please enter a target first.[/]")
            return

        self.query_one("#run-btn", Button).disabled = True
        self.query_one("#status-label", Static).update(f"Running {_TOOL_LABELS.get(self.tool_id, '')}…")

        # Dispatch in background thread
        self.run_worker(self._dispatch(target), thread=True)

    async def _dispatch(self, target: str) -> None:
        out = self.query_one("#output-area", RichLog)
        status = self.query_one("#status-label", Static)

        handlers = {
            "ai_audit":     self._run_ai_audit,
            "dns_lookup":   self._run_dns_lookup,
            "ssl_inspect":  self._run_ssl_inspect,
            "http_probe":   self._run_http_probe,
            "sec_scan":     self._run_sec_scan,
            "email_check":  self._run_email_check,
            "whois_lookup": self._run_whois_lookup,
            "tech_detect":  self._run_tech_detect,
        }

        handler = handlers.get(self.tool_id)
        if handler:
            try:
                await handler(target, out)
            except Exception as e:
                self.call_from_thread(out.write, f"\n[bold red]Error: {e}[/]")
        else:
            self.call_from_thread(out.write, f"[bold red]Unknown tool: {self.tool_id}[/]")

        self.call_from_thread(status.update, "Done. Enter another target or press ← Back.")
        self.call_from_thread(self._enable_button)

    def _enable_button(self) -> None:
        self.query_one("#run-btn", Button).disabled = False

    # ═════════════════════════════════════════════════════════════
    # Tool implementations
    # ═════════════════════════════════════════════════════════════

    async def _run_ai_audit(self, target: str, out: RichLog) -> None:
        """Full AI-Agentic audit using all registered skills."""
        self.call_from_thread(out.write, "[bold #7c3aed]═══ AI FULL AUDIT ═══[/]\n")
        self.call_from_thread(out.write, f"Target: {target}\n")

        api_key = os.getenv("LLM_API_KEY", "")
        if not api_key:
            self.call_from_thread(
                out.write,
                "[bold yellow]⚠ LLM_API_KEY not set. Agent will attempt to run but analysis may be limited.[/]\n",
            )

        from agents.llm_client import LLMClient
        from agents.audit_agent import AuditAgent

        self.call_from_thread(out.write, "🤖 Initializing AI agent and registered skills…\n")
        client = LLMClient.create(
            provider=AuditConfig.LLM_PROVIDER,
            model=AuditConfig.LLM_MODEL,
            api_key=api_key,
        )
        agent = AuditAgent(llm_client=client)

        self.call_from_thread(out.write, "🧠 Agent reasoning and orchestrating skills…\n")
        report: AuditReport = agent.run(target)

        self.call_from_thread(out.write, f"\n[bold green]✅ Audit complete in {report.total_execution_time:.2f}s[/]\n")
        self.call_from_thread(out.write, f"Skills executed: {', '.join(report.skills_executed)}\n")

        if report.dns:
            self.call_from_thread(out.write, f"\n[bold cyan]🌐 DNS[/]  IP: {report.dns.ip_address}  Consistent: {'Yes' if report.dns.is_consistent else 'No'}\n")
        if report.ssl:
            self.call_from_thread(out.write, f"[bold cyan]🔒 SSL[/]  Valid: {report.ssl.valid}  Days left: {report.ssl.days_until_expiry}\n")
        if report.performance:
            self.call_from_thread(out.write, f"[bold cyan]⚡ Perf[/] Time: {report.performance.response_time:.3f}s  Server: {report.performance.server}\n")
        if report.security:
            self.call_from_thread(out.write, f"[bold cyan]🛡️  Sec[/]  Score: {report.security.score:.0f}%  Missing: {', '.join(report.security.missing_headers) or 'None'}\n")
        if report.health_score is not None:
            self.call_from_thread(out.write, f"\n[bold magenta]🏥 AI Health Score: {report.health_score}/100[/]\n")

        if report.ai_analysis:
            self.call_from_thread(out.write, f"\n[bold magenta]═══ AI ANALYSIS ═══[/]\n{report.ai_analysis}\n")
        if report.recommendations:
            self.call_from_thread(out.write, "\n[bold cyan]💡 Recommendations:[/]\n")
            for rec in report.recommendations:
                self.call_from_thread(out.write, f"  {rec}\n")

    # ── DNS Lookup ───────────────────────────────────────────────

    async def _run_dns_lookup(self, target: str, out: RichLog) -> None:
        self.call_from_thread(out.write, f"[bold cyan]═══ DNS LOOKUP: {target} ═══[/]\n")

        # dig
        if _tool_available("dig"):
            self.call_from_thread(out.write, "\n[bold]── dig A ──[/]\n")
            result = _run_native(["dig", "+short", target, "A"])
            self.call_from_thread(out.write, result + "\n")

            self.call_from_thread(out.write, "\n[bold]── dig MX ──[/]\n")
            result = _run_native(["dig", "+short", target, "MX"])
            self.call_from_thread(out.write, result + "\n")

            self.call_from_thread(out.write, "\n[bold]── dig NS ──[/]\n")
            result = _run_native(["dig", "+short", target, "NS"])
            self.call_from_thread(out.write, result + "\n")

            self.call_from_thread(out.write, "\n[bold]── dig TXT ──[/]\n")
            result = _run_native(["dig", "+short", target, "TXT"])
            self.call_from_thread(out.write, result + "\n")
        else:
            self.call_from_thread(out.write, "[yellow]dig not available.[/]\n")

        # nslookup
        if _tool_available("nslookup"):
            self.call_from_thread(out.write, "\n[bold]── nslookup ──[/]\n")
            result = _run_native(["nslookup", target])
            self.call_from_thread(out.write, result + "\n")
        else:
            self.call_from_thread(out.write, "[yellow]nslookup not available.[/]\n")

    # ── SSL/TLS Inspector ────────────────────────────────────────

    async def _run_ssl_inspect(self, target: str, out: RichLog) -> None:
        self.call_from_thread(out.write, f"[bold cyan]═══ SSL/TLS INSPECTOR: {target} ═══[/]\n")

        if _tool_available("openssl"):
            self.call_from_thread(out.write, "\n[bold]── Certificate chain ──[/]\n")
            result = _run_native(
                ["bash", "-c", f"echo | openssl s_client -connect {target}:443 -servername {target} 2>/dev/null | openssl x509 -noout -subject -issuer -dates -fingerprint"]
            )
            self.call_from_thread(out.write, result + "\n")

            self.call_from_thread(out.write, "\n[bold]── TLS version & cipher ──[/]\n")
            result = _run_native(
                ["bash", "-c", f"echo | openssl s_client -connect {target}:443 -servername {target} 2>/dev/null | grep -E '(Protocol|Cipher|Verify)'"]
            )
            self.call_from_thread(out.write, result + "\n")

            self.call_from_thread(out.write, "\n[bold]── Subject Alternative Names (SANs) ──[/]\n")
            result = _run_native(
                ["bash", "-c", f"echo | openssl s_client -connect {target}:443 -servername {target} 2>/dev/null | openssl x509 -noout -ext subjectAltName"]
            )
            self.call_from_thread(out.write, result + "\n")
        else:
            self.call_from_thread(out.write, "[bold red]openssl is not installed.[/]\n")

    # ── HTTP Probe ───────────────────────────────────────────────

    async def _run_http_probe(self, target: str, out: RichLog) -> None:
        url = target if target.startswith(("http://", "https://")) else f"https://{target}"
        self.call_from_thread(out.write, f"[bold cyan]═══ HTTP PROBE: {url} ═══[/]\n")

        if _tool_available("curl"):
            self.call_from_thread(out.write, "\n[bold]── Status & timing ──[/]\n")
            result = _run_native([
                "curl", "-sS", "-o", "/dev/null", "-w",
                "HTTP Code: %{http_code}\n"
                "Time DNS:  %{time_namelookup}s\n"
                "Time Connect: %{time_connect}s\n"
                "Time TLS:  %{time_appconnect}s\n"
                "Time Total: %{time_total}s\n"
                "Size Download: %{size_download} bytes\n"
                "Speed Download: %{speed_download} bytes/s\n",
                "-L", url,
            ])
            self.call_from_thread(out.write, result + "\n")

            self.call_from_thread(out.write, "\n[bold]── Response headers ──[/]\n")
            result = _run_native(["curl", "-sS", "-I", "-L", url])
            self.call_from_thread(out.write, result + "\n")
        else:
            self.call_from_thread(out.write, "[bold red]curl is not installed.[/]\n")

    # ── Security Headers Scan ────────────────────────────────────

    async def _run_sec_scan(self, target: str, out: RichLog) -> None:
        url = target if target.startswith(("http://", "https://")) else f"https://{target}"
        self.call_from_thread(out.write, f"[bold cyan]═══ SECURITY HEADERS: {url} ═══[/]\n")

        from models.audit_result import SkillContext
        skill = SkillRegistry.create_skill("security_headers")
        ctx = SkillContext(domain=urlparse(url).netloc, url=url)
        result = skill.execute(ctx)

        self.call_from_thread(out.write, f"\n{result.summary}\n")
        if result.data:
            self.call_from_thread(out.write, "\n[bold]── Header Details ──[/]\n")
            for header, present in result.data.headers_present.items():
                icon = "[green]✔[/]" if present else "[red]✘[/]"
                self.call_from_thread(out.write, f"  {icon} {header}\n")

    # ── Email Domain Validator ───────────────────────────────────

    async def _run_email_check(self, target: str, out: RichLog) -> None:
        # Strip everything before @ if user typed a full email
        domain = target.split("@")[-1].strip()
        self.call_from_thread(out.write, f"[bold cyan]═══ EMAIL DOMAIN VALIDATION: {domain} ═══[/]\n")

        if _tool_available("dig"):
            # MX records
            self.call_from_thread(out.write, "\n[bold]── MX Records ──[/]\n")
            result = _run_native(["dig", "+short", domain, "MX"])
            self.call_from_thread(out.write, result + "\n")

            # SPF (TXT record starting with v=spf1)
            self.call_from_thread(out.write, "\n[bold]── SPF Record ──[/]\n")
            result = _run_native(["dig", "+short", domain, "TXT"])
            spf_found = False
            for line in result.splitlines():
                if "v=spf1" in line.lower():
                    self.call_from_thread(out.write, f"  [green]✔ SPF found:[/] {line}\n")
                    spf_found = True
            if not spf_found:
                self.call_from_thread(out.write, "  [red]✘ No SPF record found.[/]\n")

            # DKIM (check common selectors)
            self.call_from_thread(out.write, "\n[bold]── DKIM Records (common selectors) ──[/]\n")
            for selector in ["default", "google", "selector1", "selector2", "k1"]:
                dkim_domain = f"{selector}._domainkey.{domain}"
                result = _run_native(["dig", "+short", dkim_domain, "TXT"])
                if result and "no output" not in result.lower() and "nxdomain" not in result.lower():
                    self.call_from_thread(out.write, f"  [green]✔ {selector}:[/] {result[:80]}…\n")
                    break
            else:
                self.call_from_thread(out.write, "  [yellow]No DKIM record found for common selectors.[/]\n")

            # DMARC
            self.call_from_thread(out.write, "\n[bold]── DMARC Record ──[/]\n")
            result = _run_native(["dig", "+short", f"_dmarc.{domain}", "TXT"])
            if result and "no output" not in result.lower():
                self.call_from_thread(out.write, f"  [green]✔ DMARC:[/] {result}\n")
            else:
                self.call_from_thread(out.write, "  [red]✘ No DMARC record found.[/]\n")
        else:
            self.call_from_thread(out.write, "[bold red]dig is not installed — cannot validate email domain.[/]\n")

    # ── WHOIS Lookup ─────────────────────────────────────────────

    async def _run_whois_lookup(self, target: str, out: RichLog) -> None:
        self.call_from_thread(out.write, f"[bold cyan]═══ WHOIS LOOKUP: {target} ═══[/]\n")

        from models.audit_result import SkillContext
        skill = SkillRegistry.create_skill("whois_lookup")
        ctx = SkillContext(domain=target, url=f"https://{target}")
        result = skill.execute(ctx)

        self.call_from_thread(out.write, f"\n{result.summary}\n")

        if result.data and not result.data.error:
            self.call_from_thread(out.write, f"\n  Registrar:  {result.data.registrar or 'N/A'}\n")
            self.call_from_thread(out.write, f"  Created:    {result.data.creation_date or 'N/A'}\n")
            self.call_from_thread(out.write, f"  Expires:    {result.data.expiration_date or 'N/A'}\n")
            self.call_from_thread(out.write, f"  Country:    {result.data.country or 'N/A'}\n")
            if result.data.name_servers:
                self.call_from_thread(out.write, f"  NS:         {', '.join(result.data.name_servers[:4])}\n")

    # ── Tech Detection ───────────────────────────────────────────

    async def _run_tech_detect(self, target: str, out: RichLog) -> None:
        url = target if target.startswith(("http://", "https://")) else f"https://{target}"
        self.call_from_thread(out.write, f"[bold cyan]═══ TECH DETECTION: {url} ═══[/]\n")

        from models.audit_result import SkillContext
        skill = SkillRegistry.create_skill("tech_detection")
        ctx = SkillContext(domain=urlparse(url).netloc, url=url)
        result = skill.execute(ctx)

        self.call_from_thread(out.write, f"\n{result.summary}\n")


# ═══════════════════════════════════════════════════════════════════
# Entry-point
# ═══════════════════════════════════════════════════════════════════

def main() -> None:
    app = WechyApp()
    app.run()


if __name__ == "__main__":
    main()
