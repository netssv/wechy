#!/usr/bin/env python3
"""
Audit Agent — the main orchestrator.

Receives a URL from the user, reasons about which skills to run,
executes them via the agentic loop, and produces an AuditReport.
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import asdict
from typing import Any
from urllib.parse import urlparse

from agents.base_agent import BaseAgent
from agents.llm_client import BaseLLMClient
from agents.prompts import AUDIT_AGENT_SYSTEM_PROMPT
from config.settings import AuditConfig
from models.audit_result import (
    AuditReport,
    ConnectivityResult,
    SkillContext,
    SkillResult,
)
from skills.skill_registry import SkillRegistry

logger = logging.getLogger(__name__)


class AuditAgent(BaseAgent):
    """AI agent that orchestrates a web audit by autonomously selecting
    and executing agentic skills, then analysing the results."""

    def __init__(
        self,
        llm_client: BaseLLMClient,
        skill_registry: type[SkillRegistry] = SkillRegistry,
        config: type[AuditConfig] = AuditConfig,
    ):
        super().__init__(llm_client, skill_registry, config)

    # ── Public API ───────────────────────────────────────────────

    def run(self, url: str, mode: str = "comprehensive") -> AuditReport:
        """Run a full audit.

        Parameters
        ----------
        url:  target website (with or without scheme)
        mode: "quick" or "comprehensive"
        """
        start = time.time()

        # Normalise input
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        domain = urlparse(url).netloc

        # Build the skill context
        context = SkillContext(domain=domain, url=url)

        # Prepare report
        report = AuditReport(url=url, domain=domain)

        # Get tool definitions for the LLM
        tools = self.registry.get_tools_for_llm()
        tools_summary = self.registry.get_skills_summary()

        # Initialise conversation with system prompt
        system_prompt = AUDIT_AGENT_SYSTEM_PROMPT.format(available_tools=tools_summary)
        self._add_message("system", system_prompt)

        # User instruction
        user_msg = (
            f"Perform a {mode} web audit on {url} (domain: {domain}). "
            f"Use the appropriate skills to gather information and then "
            f"provide a complete analysis."
        )
        self._add_message("user", user_msg)

        # ── Agentic loop: think → act → observe ─────────────────
        iterations = 0
        max_iter = self.config.AGENT_MAX_ITERATIONS

        while iterations < max_iter:
            iterations += 1
            logger.info("Agent iteration %d/%d", iterations, max_iter)

            response = self._think(tools=tools)

            if response.has_tool_call and response.tool_name:
                # The agent decided to invoke a skill
                skill_name = response.tool_name
                logger.info("Agent calls skill: %s", skill_name)

                # Merge any extra params from the LLM into the context
                enriched_context = SkillContext(
                    domain=domain,
                    url=url,
                    raw_params=response.tool_args,
                )

                result = self._execute_skill(skill_name, enriched_context)

                # Feed the result back into the conversation
                self._add_message("assistant", f"[Calling skill: {skill_name}]")
                self._add_message("tool", result.summary)

                # Attach result to the report
                self._attach_to_report(report, skill_name, result)
                report.skills_executed.append(skill_name)

            else:
                # The agent is done reasoning — final response
                logger.info("Agent finished reasoning.")
                report.ai_analysis = response.content
                self._extract_recommendations(report, response.content)
                break

        report.total_execution_time = time.time() - start
        return report

    # ── Helpers ──────────────────────────────────────────────────

    def _attach_to_report(
        self, report: AuditReport, skill_name: str, result: SkillResult
    ) -> None:
        """Map a skill result to the appropriate report field."""
        if not result.success:
            report.errors.append(f"{skill_name}: {'; '.join(result.errors)}")
            return

        mapping = {
            "dns_analysis": "dns",
            "ssl_analysis": "ssl",
            "performance_analysis": "performance",
            "security_headers": "security",
            "whois_lookup": "whois",
            "tech_detection": "tech_detection",
        }

        field = mapping.get(skill_name)
        if field and result.data is not None:
            setattr(report, field, result.data)

    def _extract_recommendations(self, report: AuditReport, analysis: str) -> None:
        """Parse numbered recommendations from the agent's analysis text."""
        lines = analysis.split("\n")
        for line in lines:
            stripped = line.strip()
            # Look for lines starting with a number or bullet
            if stripped and (stripped[0].isdigit() or stripped.startswith(("-", "•", "→"))):
                report.recommendations.append(stripped)

        # Try to extract health score
        for line in lines:
            lower = line.lower()
            if "health score" in lower or "/100" in lower:
                # Try to find a number
                for word in line.split():
                    clean = word.strip(":/()%")
                    try:
                        score = int(clean)
                        if 0 <= score <= 100:
                            report.health_score = score
                            break
                    except ValueError:
                        continue
