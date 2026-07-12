#!/usr/bin/env python3
"""
Base Agent — abstract class for all AI agents in the system.

Provides the agentic loop skeleton (think → act → observe) and
shared utilities for LLM interaction and skill execution.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from agents.llm_client import BaseLLMClient
from config.settings import AuditConfig
from models.audit_result import AgentResponse, SkillContext, SkillResult
from skills.skill_registry import SkillRegistry

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Abstract AI agent that reasons via an LLM and acts through skills."""

    def __init__(
        self,
        llm_client: BaseLLMClient,
        skill_registry: type[SkillRegistry] = SkillRegistry,
        config: type[AuditConfig] = AuditConfig,
    ):
        self.llm = llm_client
        self.registry = skill_registry
        self.config = config
        self.conversation_history: List[Dict[str, str]] = []
        self.skill_results: List[SkillResult] = []

    # ── Abstract ─────────────────────────────────────────────────

    @abstractmethod
    def run(self, user_input: str, **kwargs: Any) -> Any:
        """Process a user instruction and return a response."""
        ...

    # ── Shared helpers ───────────────────────────────────────────

    def _add_message(self, role: str, content: str) -> None:
        self.conversation_history.append({"role": role, "content": content})

    def _think(self, tools: Optional[List[Dict[str, Any]]] = None) -> AgentResponse:
        """Ask the LLM what to do next given the conversation so far."""
        return self.llm.chat(
            messages=self.conversation_history,
            tools=tools,
            temperature=self.config.AGENT_TEMPERATURE,
        )

    def _execute_skill(self, skill_name: str, context: SkillContext) -> SkillResult:
        """Instantiate and run a skill by name."""
        skill = self.registry.create_skill(skill_name)
        validation = skill.validate_input(context)
        if not validation.valid:
            return SkillResult(
                skill_name=skill_name,
                success=False,
                summary=f"Validation failed: {'; '.join(validation.errors)}",
                errors=validation.errors,
            )
        result = skill.execute(context)
        self.skill_results.append(result)
        return result
