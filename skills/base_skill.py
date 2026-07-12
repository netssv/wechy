#!/usr/bin/env python3
"""
Base class for all agentic skills.

Every skill self-describes so the AI agent can:
  1. DISCOVER it   — know it exists (via SkillRegistry)
  2. UNDERSTAND it — know what it does and when to use it
  3. EXECUTE it    — invoke it with the right parameters
  4. INTERPRET it  — understand the result it returns
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from models.audit_result import SkillContext, SkillResult, ValidationResult


class BaseSkill(ABC):
    """Abstract base class that every agentic skill must implement.

    The metadata attributes (name, description, category …) are read
    by the agent's LLM via ``get_tool_definition()`` so it can decide
    autonomously whether and when to invoke this skill.
    """

    # ── Agentic metadata (subclasses MUST override) ──────────────
    name: str = ""
    display_name: str = ""
    description: str = ""          # Natural-language description for the LLM
    category: str = ""             # e.g. "network", "security", "performance"

    required_inputs: List[str] = []
    optional_inputs: List[str] = []
    output_description: str = ""   # What the skill returns, in plain language

    estimated_time: str = ""       # Human-readable estimate, e.g. "2-5 seconds"
    priority: int = 3              # 1 = highest, 5 = lowest

    # ── Core methods ─────────────────────────────────────────────

    @abstractmethod
    def execute(self, context: SkillContext) -> SkillResult:
        """Run the skill and return a structured result.

        The agent calls this after deciding it needs this skill.
        """
        ...

    @abstractmethod
    def validate_input(self, context: SkillContext) -> ValidationResult:
        """Check whether the context provides everything the skill needs."""
        ...

    # ── Agentic interface ────────────────────────────────────────

    def get_tool_definition(self) -> Dict[str, Any]:
        """Return a function-calling-compatible tool definition.

        This is what gets passed to the LLM so it can invoke the skill
        through the ``tools`` / ``functions`` parameter.
        """
        properties: Dict[str, Any] = {}
        for inp in self.required_inputs:
            properties[inp] = {"type": "string", "description": f"Required: {inp}"}
        for inp in self.optional_inputs:
            properties[inp] = {"type": "string", "description": f"Optional: {inp}"}

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": self.required_inputs,
                },
            },
        }

    def get_summary(self) -> str:
        """One-line summary for display purposes."""
        return f"[{self.category}] {self.display_name} — {self.description[:80]}"

    # ── Helpers ───────────────────────────────────────────────────

    def _validate_required(self, context: SkillContext) -> ValidationResult:
        """Utility: check that all required_inputs exist in the context."""
        errors: List[str] = []
        for inp in self.required_inputs:
            if context.get(inp) is None:
                errors.append(f"Missing required input: '{inp}'")
        return ValidationResult(valid=len(errors) == 0, errors=errors)

    def __repr__(self) -> str:
        return f"<Skill:{self.name} [{self.category}] prio={self.priority}>"
