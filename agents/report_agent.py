#!/usr/bin/env python3
"""
Report Agent — generates professional audit reports.

Takes raw skill results and uses the LLM to produce a structured,
human-readable report with recommendations and a health score.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict
from typing import Any

from agents.base_agent import BaseAgent
from agents.llm_client import BaseLLMClient
from agents.prompts import REPORT_AGENT_SYSTEM_PROMPT
from config.settings import AuditConfig
from models.audit_result import AuditReport
from skills.skill_registry import SkillRegistry

logger = logging.getLogger(__name__)


class ReportAgent(BaseAgent):
    """AI agent specialised in generating clear, actionable audit reports."""

    def __init__(
        self,
        llm_client: BaseLLMClient,
        skill_registry: type[SkillRegistry] = SkillRegistry,
        config: type[AuditConfig] = AuditConfig,
    ):
        super().__init__(llm_client, skill_registry, config)

    def run(self, user_input: str, **kwargs: Any) -> str:
        """Generate a report from an existing AuditReport.

        Parameters
        ----------
        user_input: additional instructions (e.g. "focus on security")
        report:     AuditReport instance (passed as kwarg)
        """
        report: AuditReport | None = kwargs.get("report")
        if report is None:
            return "No audit report provided."

        # Serialise report data for the LLM
        report_data = self._serialise_report(report)

        self._add_message("system", REPORT_AGENT_SYSTEM_PROMPT)
        self._add_message(
            "user",
            f"Generate a professional audit report based on the following data:\n\n"
            f"```json\n{report_data}\n```\n\n"
            f"Additional instructions: {user_input or 'none'}",
        )

        response = self._think()
        return response.content

    @staticmethod
    def _serialise_report(report: AuditReport) -> str:
        """Convert an AuditReport to a JSON string, handling non-serialisable types."""
        try:
            data = asdict(report)
            return json.dumps(data, indent=2, default=str)
        except Exception:
            # Fallback: build a simpler dict
            summary = {
                "url": report.url,
                "domain": report.domain,
                "skills_executed": report.skills_executed,
                "errors": report.errors,
                "total_execution_time": report.total_execution_time,
            }
            return json.dumps(summary, indent=2, default=str)
