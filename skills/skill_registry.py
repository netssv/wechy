#!/usr/bin/env python3
"""
Skill Registry — dynamic discovery and management of agentic skills.

The agent queries this registry to know what tools it has available.
Skills auto-register themselves using the ``@SkillRegistry.register``
decorator, so adding a new skill requires zero changes to the agent.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Type

from skills.base_skill import BaseSkill

logger = logging.getLogger(__name__)


class SkillRegistry:
    """Central catalogue of agentic skills.

    Usage::

        @SkillRegistry.register
        class MySkill(BaseSkill):
            name = "my_skill"
            ...

        # Later, the agent can query:
        tools = SkillRegistry.get_tools_for_llm()
        skill = SkillRegistry.create_skill("my_skill")
    """

    _skills: Dict[str, Type[BaseSkill]] = {}

    # ── Registration ─────────────────────────────────────────────

    @classmethod
    def register(cls, skill_class: Type[BaseSkill]) -> Type[BaseSkill]:
        """Register a skill class.  Can be used as a decorator."""
        if not skill_class.name:
            raise ValueError(
                f"{skill_class.__name__} must define a non-empty 'name' attribute."
            )
        cls._skills[skill_class.name] = skill_class
        logger.info("Registered skill: %s (%s)", skill_class.name, skill_class.display_name)
        return skill_class

    @classmethod
    def unregister(cls, name: str) -> None:
        """Remove a skill from the registry."""
        cls._skills.pop(name, None)

    # ── Discovery (used by agents) ───────────────────────────────

    @classmethod
    def get_available_skills(cls) -> List[str]:
        """Return the names of all registered skills."""
        return list(cls._skills.keys())

    @classmethod
    def get_skill_class(cls, name: str) -> Optional[Type[BaseSkill]]:
        """Get a skill class by name."""
        return cls._skills.get(name)

    @classmethod
    def create_skill(cls, name: str, **kwargs: Any) -> BaseSkill:
        """Instantiate a registered skill by name."""
        skill_class = cls._skills.get(name)
        if skill_class is None:
            raise KeyError(f"Skill '{name}' is not registered. Available: {cls.get_available_skills()}")
        return skill_class(**kwargs)

    @classmethod
    def get_all_skills(cls) -> List[BaseSkill]:
        """Instantiate and return all registered skills."""
        return [skill_class() for skill_class in cls._skills.values()]

    @classmethod
    def get_skills_by_category(cls, category: str) -> List[Type[BaseSkill]]:
        """Filter skill classes by category."""
        return [
            s for s in cls._skills.values()
            if s.category == category
        ]

    @classmethod
    def get_skills_by_priority(cls, max_priority: int = 5) -> List[BaseSkill]:
        """Return skills with priority <= max_priority, sorted by priority."""
        skills = [
            skill_class()
            for skill_class in cls._skills.values()
            if skill_class.priority <= max_priority
        ]
        return sorted(skills, key=lambda s: s.priority)

    # ── LLM integration ─────────────────────────────────────────

    @classmethod
    def get_tools_for_llm(cls) -> List[Dict[str, Any]]:
        """Generate the list of tool definitions for the LLM.

        This is what gets passed to the model's ``tools`` parameter
        so the agent knows what skills it can invoke.
        """
        tools = []
        for skill_class in cls._skills.values():
            skill = skill_class()
            tools.append(skill.get_tool_definition())
        return tools

    @classmethod
    def get_skills_summary(cls) -> str:
        """Human-readable summary of all skills (useful for system prompts)."""
        lines = []
        for skill_class in cls._skills.values():
            skill = skill_class()
            lines.append(f"• {skill.display_name}: {skill.description}")
        return "\n".join(lines)

    # ── Utilities ────────────────────────────────────────────────

    @classmethod
    def clear(cls) -> None:
        """Remove all registered skills (mainly for testing)."""
        cls._skills.clear()

    @classmethod
    def count(cls) -> int:
        """Number of registered skills."""
        return len(cls._skills)

    @classmethod
    def __repr__(cls) -> str:
        return f"<SkillRegistry skills={cls.get_available_skills()}>"
