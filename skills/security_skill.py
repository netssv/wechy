#!/usr/bin/env python3
"""
Security Headers Agentic Skill

Evaluates HTTP security headers (HSTS, CSP, X-Frame-Options, etc.)
and calculates a security score.

The agent uses this skill to assess the security posture of a website
and generate actionable hardening recommendations.
"""

import time

import requests

from config.settings import AuditConfig
from models.audit_result import SecurityResult, SkillContext, SkillResult, ValidationResult
from skills.base_skill import BaseSkill
from skills.skill_registry import SkillRegistry

# Headers that a well-configured site should have
_SECURITY_HEADERS = [
    "Strict-Transport-Security",
    "X-Content-Type-Options",
    "X-Frame-Options",
    "X-XSS-Protection",
    "Content-Security-Policy",
    "Referrer-Policy",
]


@SkillRegistry.register
class SecuritySkill(BaseSkill):
    """Agentic skill for HTTP security headers analysis."""

    # ── Agentic metadata ─────────────────────────────────────────
    name = "security_headers"
    display_name = "Security Headers Analysis"
    description = (
        "Evaluates the HTTP security headers of a website: "
        "Strict-Transport-Security (HSTS), Content-Security-Policy (CSP), "
        "X-Frame-Options, X-Content-Type-Options, X-XSS-Protection, "
        "and Referrer-Policy. Calculates a security score (0-100%) "
        "and lists missing headers. Use this to assess the security "
        "posture of a site and generate hardening recommendations."
    )
    category = "security"
    required_inputs = ["url"]
    optional_inputs = []
    output_description = (
        "Per-header presence check, overall security score, and "
        "list of missing headers with explanations."
    )
    estimated_time = "1-3 seconds"
    priority = 2

    # ── Execution ────────────────────────────────────────────────

    def validate_input(self, context: SkillContext) -> ValidationResult:
        url = context.get("url")
        if not url:
            return ValidationResult(valid=False, errors=["Missing required input: 'url'"])
        return ValidationResult(valid=True)

    def execute(self, context: SkillContext) -> SkillResult:
        url = context.get("url")
        start = time.time()

        try:
            response = requests.get(url, timeout=AuditConfig.DEFAULT_TIMEOUT)
            headers = {k.lower(): v for k, v in response.headers.items()}

            headers_present = {}
            for header in _SECURITY_HEADERS:
                headers_present[header] = header.lower() in headers

            total = len(_SECURITY_HEADERS)
            present = sum(headers_present.values())
            score = (present / total) * 100 if total else 0
            missing = [h for h, ok in headers_present.items() if not ok]

            sec_result = SecurityResult(
                headers_present=headers_present,
                score=score,
                total_headers=total,
                present_count=present,
                missing_headers=missing,
            )

            if score >= 80:
                verdict = "🟢 GOOD"
            elif score >= 50:
                verdict = "🟡 MODERATE"
            else:
                verdict = "🔴 POOR"

            summary = (
                f"Security score: {score:.0f}% ({verdict}). "
                f"{present}/{total} headers present. "
                f"Missing: {', '.join(missing) if missing else 'none'}."
            )

            return SkillResult(
                skill_name=self.name,
                success=True,
                data=sec_result,
                summary=summary,
                execution_time=time.time() - start,
            )

        except Exception as e:
            return SkillResult(
                skill_name=self.name,
                success=False,
                summary=f"Security analysis failed for '{url}': {e}",
                errors=[str(e)],
                execution_time=time.time() - start,
            )
