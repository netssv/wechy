#!/usr/bin/env python3
"""
WHOIS Agentic Skill

Retrieves domain registration information: registrar, creation date,
expiration date, name servers, and status.

The agent uses this skill to investigate domain ownership, detect
expiring domains, or verify domain legitimacy.
"""

import time

import whois

from models.audit_result import WHOISResult, SkillContext, SkillResult, ValidationResult
from skills.base_skill import BaseSkill
from skills.skill_registry import SkillRegistry


@SkillRegistry.register
class WHOISSkill(BaseSkill):
    """Agentic skill for WHOIS domain registration lookup."""

    # ── Agentic metadata ─────────────────────────────────────────
    name = "whois_lookup"
    display_name = "WHOIS Domain Lookup"
    description = (
        "Retrieves WHOIS registration information for a domain: "
        "registrar, creation date, expiration date, name servers, "
        "registration status, and registrant country. Use this to "
        "investigate domain ownership, detect domains about to expire, "
        "or verify the legitimacy of a domain."
    )
    category = "domain_info"
    required_inputs = ["domain"]
    optional_inputs = []
    output_description = (
        "Registrar, creation/expiration dates, name servers, "
        "registration status, and country."
    )
    estimated_time = "2-5 seconds"
    priority = 4

    # ── Execution ────────────────────────────────────────────────

    def validate_input(self, context: SkillContext) -> ValidationResult:
        return self._validate_required(context)

    def execute(self, context: SkillContext) -> SkillResult:
        domain = context.get("domain")
        start = time.time()

        try:
            w = whois.whois(domain)

            whois_result = WHOISResult(
                registrar=w.registrar,
                creation_date=w.creation_date,
                expiration_date=w.expiration_date,
                name_servers=w.name_servers or [],
                status=w.status,
                country=getattr(w, "country", None),
            )

            registrar_str = w.registrar or "Unknown"
            expiry_str = str(w.expiration_date) if w.expiration_date else "Unknown"
            summary = (
                f"Domain '{domain}' registered with {registrar_str}. "
                f"Expires: {expiry_str}. "
                f"Name servers: {', '.join((w.name_servers or [])[:3])}."
            )

            return SkillResult(
                skill_name=self.name,
                success=True,
                data=whois_result,
                summary=summary,
                execution_time=time.time() - start,
            )

        except Exception as e:
            return SkillResult(
                skill_name=self.name,
                success=False,
                data=WHOISResult(error=str(e)),
                summary=f"WHOIS lookup failed for '{domain}': {e}",
                errors=[str(e)],
                execution_time=time.time() - start,
            )
