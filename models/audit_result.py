#!/usr/bin/env python3
"""
Data models for the Enhanced Web Audit system.

Provides typed dataclasses for all audit results, skill I/O,
and agent responses. Replaces the raw dict-based approach from
the monolithic WebAuditor class.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


# ═══════════════════════════════════════════════════════════════════
# Enums
# ═══════════════════════════════════════════════════════════════════

class AuditStatus(Enum):
    """Overall status for any check."""
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    SKIPPED = "skipped"


class PerformanceRating(Enum):
    """Response-time based rating."""
    EXCELLENT = "excellent"
    GOOD = "good"
    SLOW = "slow"
    VERY_SLOW = "very_slow"


# ═══════════════════════════════════════════════════════════════════
# Skill I/O models  (used by the agentic skill system)
# ═══════════════════════════════════════════════════════════════════

@dataclass
class SkillContext:
    """Input context passed to every skill execution.

    The agent populates this before invoking a skill so the skill
    has everything it needs without reaching outside its scope.
    """
    domain: str
    url: str
    raw_params: Dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        """Convenience accessor that checks raw_params first,
        then falls back to top-level attributes."""
        if key in self.raw_params:
            return self.raw_params[key]
        return getattr(self, key, default)


@dataclass
class ValidationResult:
    """Result of a skill's input validation."""
    valid: bool
    errors: List[str] = field(default_factory=list)


@dataclass
class SkillResult:
    """Standardised output returned by every agentic skill.

    The ``summary`` field is crucial — the agent reads it to reason
    about the next step.
    """
    skill_name: str
    success: bool
    data: Any = None
    summary: str = ""
    errors: List[str] = field(default_factory=list)
    execution_time: float = 0.0

    def to_message(self) -> Dict[str, str]:
        """Convert to a chat-style message for the agent's
        conversation history."""
        return {
            "role": "tool",
            "name": self.skill_name,
            "content": self.summary if self.success else f"Error: {'; '.join(self.errors)}",
        }


# ═══════════════════════════════════════════════════════════════════
# DNS models
# ═══════════════════════════════════════════════════════════════════

@dataclass
class PropagationEntry:
    """Single DNS propagation check against one nameserver."""
    server_name: str
    server_ip: str
    resolved_ip: Optional[str]
    response_time: Optional[float]
    status: AuditStatus
    error: Optional[str] = None


@dataclass
class DNSResult:
    """Complete DNS analysis output."""
    domain: str
    ip_address: Optional[str]
    records: Dict[str, List[str]] = field(default_factory=dict)
    propagation: List[PropagationEntry] = field(default_factory=list)
    is_consistent: bool = True
    unique_ips: int = 0


# ═══════════════════════════════════════════════════════════════════
# SSL models
# ═══════════════════════════════════════════════════════════════════

@dataclass
class SSLResult:
    """SSL/TLS certificate analysis output."""
    valid: bool
    issuer: Optional[Dict[str, str]] = None
    subject: Optional[Dict[str, str]] = None
    not_before: Optional[datetime] = None
    not_after: Optional[datetime] = None
    days_until_expiry: Optional[int] = None
    serial_number: Optional[str] = None
    version: Optional[int] = None
    subject_alt_names: List[str] = field(default_factory=list)
    error: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════
# Performance models
# ═══════════════════════════════════════════════════════════════════

@dataclass
class PerformanceResult:
    """Website performance metrics."""
    response_time: Optional[float] = None
    status_code: Optional[int] = None
    content_length: Optional[int] = None
    compression_enabled: bool = False
    cache_control: str = ""
    etag: bool = False
    last_modified: bool = False
    server: str = "Unknown"
    rating: PerformanceRating = PerformanceRating.GOOD
    headers: Dict[str, str] = field(default_factory=dict)
    error: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════
# Security models
# ═══════════════════════════════════════════════════════════════════

@dataclass
class SecurityResult:
    """Security headers analysis output."""
    headers_present: Dict[str, bool] = field(default_factory=dict)
    score: float = 0.0
    total_headers: int = 0
    present_count: int = 0
    missing_headers: List[str] = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════
# WHOIS models
# ═══════════════════════════════════════════════════════════════════

@dataclass
class WHOISResult:
    """WHOIS domain registration data."""
    registrar: Optional[str] = None
    creation_date: Optional[Any] = None
    expiration_date: Optional[Any] = None
    name_servers: List[str] = field(default_factory=list)
    status: Optional[Any] = None
    country: Optional[str] = None
    error: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════
# Technology detection models
# ═══════════════════════════════════════════════════════════════════

@dataclass
class TechDetectionResult:
    """Detected web technologies."""
    technologies: List[str] = field(default_factory=list)
    server: Optional[str] = None
    powered_by: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════
# Connectivity model
# ═══════════════════════════════════════════════════════════════════

@dataclass
class ConnectivityResult:
    """Basic reachability check."""
    accessible: bool = False
    status_code: Optional[int] = None
    response_time: Optional[float] = None
    final_url: Optional[str] = None
    redirected: bool = False
    error: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════
# Agent response model
# ═══════════════════════════════════════════════════════════════════

@dataclass
class AgentResponse:
    """Response produced by an AI agent."""
    content: str
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    has_tool_call: bool = False
    tool_name: Optional[str] = None
    tool_args: Dict[str, Any] = field(default_factory=dict)
    finish_reason: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════
# Top-level audit report
# ═══════════════════════════════════════════════════════════════════

@dataclass
class AuditReport:
    """Complete audit report aggregating all skill results
    plus the AI agent's analysis."""
    url: str
    domain: str
    timestamp: datetime = field(default_factory=datetime.now)

    # Skill results (populated as the agent runs skills)
    connectivity: Optional[ConnectivityResult] = None
    dns: Optional[DNSResult] = None
    ssl: Optional[SSLResult] = None
    performance: Optional[PerformanceResult] = None
    security: Optional[SecurityResult] = None
    whois: Optional[WHOISResult] = None
    tech_detection: Optional[TechDetectionResult] = None

    # AI-generated content
    ai_analysis: Optional[str] = None
    recommendations: List[str] = field(default_factory=list)
    health_score: Optional[int] = None  # 0-100

    # Metadata
    skills_executed: List[str] = field(default_factory=list)
    total_execution_time: float = 0.0
    errors: List[str] = field(default_factory=list)
