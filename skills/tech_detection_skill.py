#!/usr/bin/env python3
"""
Technology Detection Agentic Skill

Detects web technologies: server software, backend framework,
CMS (WordPress, Drupal, …), and front-end libraries (React, Vue, …).

The agent uses this skill to understand the tech stack of a website,
which informs security and performance recommendations.
"""

import time

import requests

from config.settings import AuditConfig
from models.audit_result import TechDetectionResult, SkillContext, SkillResult, ValidationResult
from skills.base_skill import BaseSkill
from skills.skill_registry import SkillRegistry


@SkillRegistry.register
class TechDetectionSkill(BaseSkill):
    """Agentic skill for web technology fingerprinting."""

    # ── Agentic metadata ─────────────────────────────────────────
    name = "tech_detection"
    display_name = "Technology Detection"
    description = (
        "Detects the web technologies used by a website: server software "
        "(Nginx, Apache, Cloudflare, IIS), backend framework (PHP, ASP.NET), "
        "CMS (WordPress, Drupal, Joomla), and front-end libraries "
        "(React, Vue.js, Angular). Use this to understand the tech stack, "
        "which helps tailor security and performance recommendations."
    )
    category = "analysis"
    required_inputs = ["url"]
    optional_inputs = []
    output_description = (
        "List of detected technologies, server software, and "
        "X-Powered-By value."
    )
    estimated_time = "1-3 seconds"
    priority = 4

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
            content = response.text.lower()
            technologies = []

            # Server detection
            server = headers.get("server", "").lower()
            server_display = headers.get("server", "Unknown")
            if "nginx" in server:
                technologies.append("Nginx")
            elif "apache" in server:
                technologies.append("Apache")
            elif "cloudflare" in server:
                technologies.append("Cloudflare")
            elif "microsoft-iis" in server:
                technologies.append("Microsoft IIS")

            # Backend framework
            powered_by = headers.get("x-powered-by", "")
            if powered_by:
                pb_lower = powered_by.lower()
                if "php" in pb_lower:
                    technologies.append("PHP")
                elif "asp.net" in pb_lower:
                    technologies.append("ASP.NET")
                elif "express" in pb_lower:
                    technologies.append("Express.js")

            # CMS detection
            if "wordpress" in content or "wp-content" in content:
                technologies.append("WordPress")
            elif "drupal" in content:
                technologies.append("Drupal")
            elif "joomla" in content:
                technologies.append("Joomla")

            # Front-end frameworks
            if "react" in content or "reactdom" in content:
                technologies.append("React")
            if "vue" in content or "__vue__" in content:
                technologies.append("Vue.js")
            if "angular" in content or "ng-version" in content:
                technologies.append("Angular")

            tech_result = TechDetectionResult(
                technologies=technologies,
                server=server_display,
                powered_by=powered_by or None,
            )

            tech_list = ", ".join(technologies) if technologies else "no specific technologies detected"
            summary = (
                f"Server: {server_display}. "
                f"Detected technologies: {tech_list}."
            )

            return SkillResult(
                skill_name=self.name,
                success=True,
                data=tech_result,
                summary=summary,
                execution_time=time.time() - start,
            )

        except Exception as e:
            return SkillResult(
                skill_name=self.name,
                success=False,
                summary=f"Technology detection failed for '{url}': {e}",
                errors=[str(e)],
                execution_time=time.time() - start,
            )
