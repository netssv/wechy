#!/usr/bin/env python3
"""
Centralised configuration for the Enhanced Web Audit system.

All tunables (timeouts, thresholds, LLM settings) live here so they
can be changed without touching business logic or skill code.
"""

import os


class AuditConfig:
    """Global configuration constants."""

    # ── Network ──────────────────────────────────────────────────
    DEFAULT_TIMEOUT: int = 10          # seconds for generic HTTP requests
    DNS_TIMEOUT: int = 5               # seconds per DNS query
    MAX_WORKERS: int = 10              # ThreadPoolExecutor concurrency

    # ── Performance thresholds (seconds) ─────────────────────────
    PERFORMANCE_THRESHOLDS = {
        "excellent": 1.0,
        "good": 3.0,
    }

    # ── LLM / Agent ─────────────────────────────────────────────
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "google")        # google | openai | ollama
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gemini-2.0-flash")
    LLM_API_KEY: str | None = os.getenv("LLM_API_KEY")             # read from env
    AGENT_TEMPERATURE: float = 0.3     # low for deterministic reasoning
    AGENT_MAX_ITERATIONS: int = 10     # max think→act→observe loops

    # ── Logging ──────────────────────────────────────────────────
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
