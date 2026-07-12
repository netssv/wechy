#!/usr/bin/env python3
"""
Performance Agentic Skill

Measures website performance: response time, content size,
compression status, and caching headers.

The agent uses this skill to evaluate site speed and optimisation.
"""

import time

import requests

from config.settings import AuditConfig
from models.audit_result import (
    PerformanceRating,
    PerformanceResult,
    SkillContext,
    SkillResult,
    ValidationResult,
)
from skills.base_skill import BaseSkill
from skills.skill_registry import SkillRegistry


@SkillRegistry.register
class PerformanceSkill(BaseSkill):
    """Agentic skill for website performance analysis."""

    # ── Agentic metadata ─────────────────────────────────────────
    name = "performance_analysis"
    display_name = "Performance Analysis"
    description = (
        "Measures website performance metrics: HTTP response time, "
        "content size, compression (gzip/brotli), caching headers "
        "(Cache-Control, ETag, Last-Modified), and identifies the "
        "web server. Use this to evaluate site speed, check if "
        "optimisation best practices are in place, and diagnose "
        "slow loading times."
    )
    category = "performance"
    required_inputs = ["url"]
    optional_inputs = []
    output_description = (
        "Response time, status code, content size, compression status, "
        "caching headers, web server, and a performance rating."
    )
    estimated_time = "2-5 seconds"
    priority = 3

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
            response = requests.get(url, timeout=30)
            total_time = time.time() - start

            headers = dict(response.headers)
            content_length = len(response.content)
            compression = "gzip" in headers.get("content-encoding", "").lower()
            cache_control = headers.get("cache-control", "")

            # Determine rating
            thresholds = AuditConfig.PERFORMANCE_THRESHOLDS
            if total_time < thresholds["excellent"]:
                rating = PerformanceRating.EXCELLENT
            elif total_time < thresholds["good"]:
                rating = PerformanceRating.GOOD
            else:
                rating = PerformanceRating.SLOW

            perf_result = PerformanceResult(
                response_time=total_time,
                status_code=response.status_code,
                content_length=content_length,
                compression_enabled=compression,
                cache_control=cache_control,
                etag=bool(headers.get("etag", "")),
                last_modified=bool(headers.get("last-modified", "")),
                server=headers.get("server", "Unknown"),
                rating=rating,
                headers=headers,
            )

            size_kb = content_length / 1024
            summary = (
                f"Response time: {total_time:.3f}s ({rating.value}). "
                f"Status: {response.status_code}. "
                f"Size: {size_kb:.1f} KB. "
                f"Compression: {'enabled' if compression else 'NOT enabled'}. "
                f"Cache-Control: {cache_control or 'not set'}. "
                f"Server: {perf_result.server}."
            )

            return SkillResult(
                skill_name=self.name,
                success=True,
                data=perf_result,
                summary=summary,
                execution_time=time.time() - start,
            )

        except Exception as e:
            return SkillResult(
                skill_name=self.name,
                success=False,
                data=PerformanceResult(error=str(e)),
                summary=f"Performance analysis failed for '{url}': {e}",
                errors=[str(e)],
                execution_time=time.time() - start,
            )
