#!/usr/bin/env python3
"""
SSL Agentic Skill

Analyses the SSL/TLS certificate of a domain: validity, issuer,
expiration, Subject Alternative Names, and version.

The agent uses this skill to check certificate health, detect
expiring certificates, or verify HTTPS setup.
"""

import socket
import ssl
import time
from datetime import datetime

from config.settings import AuditConfig
from models.audit_result import SSLResult, SkillContext, SkillResult, ValidationResult
from skills.base_skill import BaseSkill
from skills.skill_registry import SkillRegistry


@SkillRegistry.register
class SSLSkill(BaseSkill):
    """Agentic skill for SSL/TLS certificate analysis."""

    # ── Agentic metadata ─────────────────────────────────────────
    name = "ssl_analysis"
    display_name = "SSL Certificate Analysis"
    description = (
        "Analyses the SSL/TLS certificate of a domain. Returns issuer, "
        "subject, validity dates, days until expiry, serial number, "
        "version and Subject Alternative Names. Use this to verify "
        "HTTPS setup, detect expiring or invalid certificates, and "
        "assess transport-layer security."
    )
    category = "security"
    required_inputs = ["domain"]
    optional_inputs = []
    output_description = (
        "Certificate validity, issuer, subject, expiry date, days "
        "remaining, SANs and version number."
    )
    estimated_time = "1-3 seconds"
    priority = 2

    # ── Execution ────────────────────────────────────────────────

    def validate_input(self, context: SkillContext) -> ValidationResult:
        return self._validate_required(context)

    def execute(self, context: SkillContext) -> SkillResult:
        domain = context.get("domain")
        start = time.time()

        try:
            ctx = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=AuditConfig.DEFAULT_TIMEOUT) as sock:
                with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()

                    not_before = datetime.strptime(cert["notBefore"], "%b %d %H:%M:%S %Y %Z")
                    not_after = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
                    days_left = (not_after - datetime.now()).days

                    ssl_result = SSLResult(
                        valid=True,
                        issuer=dict(x[0] for x in cert["issuer"]),
                        subject=dict(x[0] for x in cert["subject"]),
                        not_before=not_before,
                        not_after=not_after,
                        days_until_expiry=days_left,
                        serial_number=cert.get("serialNumber"),
                        version=cert.get("version"),
                        subject_alt_names=[x[1] for x in cert.get("subjectAltName", [])],
                    )

                    # Build agent-readable summary
                    if days_left < 30:
                        urgency = "🚨 CRITICAL — expires very soon!"
                    elif days_left < 90:
                        urgency = "⚠️ WARNING — approaching expiry."
                    else:
                        urgency = "✅ Healthy validity period."

                    issuer_org = ssl_result.issuer.get("organizationName", "Unknown")
                    summary = (
                        f"SSL certificate for '{domain}' is VALID. "
                        f"Issuer: {issuer_org}. "
                        f"Expires: {not_after.strftime('%Y-%m-%d')} "
                        f"({days_left} days left). {urgency}"
                    )

                    return SkillResult(
                        skill_name=self.name,
                        success=True,
                        data=ssl_result,
                        summary=summary,
                        execution_time=time.time() - start,
                    )

        except Exception as e:
            return SkillResult(
                skill_name=self.name,
                success=False,
                data=SSLResult(valid=False, error=str(e)),
                summary=f"SSL analysis failed for '{domain}': {e}",
                errors=[str(e)],
                execution_time=time.time() - start,
            )
