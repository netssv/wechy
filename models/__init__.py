"""
Models module - Data classes for audit results and agent responses.
"""

from .audit_result import (
    AuditReport,
    DNSResult,
    SSLResult,
    PerformanceResult,
    SecurityResult,
    WHOISResult,
    TechDetectionResult,
    PropagationEntry,
    SkillResult,
    SkillContext,
    ValidationResult,
    AgentResponse,
)

__all__ = [
    "AuditReport",
    "DNSResult",
    "SSLResult",
    "PerformanceResult",
    "SecurityResult",
    "WHOISResult",
    "TechDetectionResult",
    "PropagationEntry",
    "SkillResult",
    "SkillContext",
    "ValidationResult",
    "AgentResponse",
]
