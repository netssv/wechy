#!/usr/bin/env python3
"""
DNS Agentic Skill

Resolves a domain, retrieves DNS records (A, AAAA, MX, NS, TXT, CNAME, SOA),
and checks propagation across global DNS servers.

The agent uses this skill when it needs to verify domain resolution,
diagnose DNS issues, or check recent DNS changes.
"""

import socket
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

import dns.resolver

from config.dns_servers import GLOBAL_DNS_SERVERS
from config.settings import AuditConfig
from models.audit_result import (
    AuditStatus,
    DNSResult,
    PropagationEntry,
    SkillContext,
    SkillResult,
    ValidationResult,
)
from skills.base_skill import BaseSkill
from skills.skill_registry import SkillRegistry


@SkillRegistry.register
class DNSSkill(BaseSkill):
    """Agentic skill for DNS resolution and global propagation analysis."""

    # ── Agentic metadata ─────────────────────────────────────────
    name = "dns_analysis"
    display_name = "DNS Analysis & Propagation"
    description = (
        "Resolves a domain to its IP address, retrieves DNS records "
        "(A, AAAA, MX, NS, TXT, CNAME, SOA), and verifies global "
        "propagation across 16 DNS servers in 6 world regions. "
        "Use this when you need to verify domain resolution, "
        "diagnose DNS problems, or check recent DNS changes."
    )
    category = "network"
    required_inputs = ["domain"]
    optional_inputs = ["record_types", "dns_servers"]
    output_description = (
        "Resolved IP, DNS records by type, and global propagation "
        "status with per-server response times."
    )
    estimated_time = "3-8 seconds"
    priority = 1

    # ── Execution ────────────────────────────────────────────────

    def validate_input(self, context: SkillContext) -> ValidationResult:
        return self._validate_required(context)

    def execute(self, context: SkillContext) -> SkillResult:
        domain = context.get("domain")
        start = time.time()

        try:
            # 1. Resolve domain
            ip_address = self._resolve_domain(domain)

            # 2. Get DNS records
            record_types = context.get("record_types", ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA"])
            records = self._get_dns_records(domain, record_types)

            # 3. Check propagation
            servers = context.get("dns_servers", GLOBAL_DNS_SERVERS)
            propagation = self._check_propagation(domain, servers)

            # Calculate consistency
            resolved_ips = {e.resolved_ip for e in propagation if e.resolved_ip}
            is_consistent = len(resolved_ips) <= 1

            dns_result = DNSResult(
                domain=domain,
                ip_address=ip_address,
                records=records,
                propagation=propagation,
                is_consistent=is_consistent,
                unique_ips=len(resolved_ips),
            )

            successful = sum(1 for e in propagation if e.status == AuditStatus.SUCCESS)
            summary = (
                f"Domain '{domain}' resolves to {ip_address or 'FAILED'}. "
                f"Propagation: {successful}/{len(propagation)} servers responded. "
                f"{'Consistent' if is_consistent else f'INCONSISTENT — {len(resolved_ips)} unique IPs'}."
            )

            return SkillResult(
                skill_name=self.name,
                success=True,
                data=dns_result,
                summary=summary,
                execution_time=time.time() - start,
            )

        except Exception as e:
            return SkillResult(
                skill_name=self.name,
                success=False,
                summary=f"DNS analysis failed for '{domain}'",
                errors=[str(e)],
                execution_time=time.time() - start,
            )

    # ── Private helpers ──────────────────────────────────────────

    def _resolve_domain(self, domain: str) -> str | None:
        try:
            return socket.gethostbyname(domain)
        except socket.gaierror:
            return None

    def _get_dns_records(self, domain: str, record_types: List[str]) -> dict:
        records = {}
        for rtype in record_types:
            try:
                resolver = dns.resolver.Resolver()
                answers = resolver.resolve(domain, rtype)
                records[rtype] = [str(a) for a in answers]
            except Exception:
                records[rtype] = []
        return records

    def _check_propagation(self, domain: str, servers: dict) -> List[PropagationEntry]:
        entries: List[PropagationEntry] = []

        def query(server_name: str, server_ip: str) -> PropagationEntry:
            try:
                resolver = dns.resolver.Resolver()
                resolver.nameservers = [server_ip]
                resolver.timeout = AuditConfig.DNS_TIMEOUT
                resolver.lifetime = AuditConfig.DNS_TIMEOUT
                t0 = time.time()
                answer = resolver.resolve(domain, "A")
                elapsed = time.time() - t0
                return PropagationEntry(
                    server_name=server_name,
                    server_ip=server_ip,
                    resolved_ip=str(answer[0]),
                    response_time=elapsed,
                    status=AuditStatus.SUCCESS,
                )
            except Exception as exc:
                return PropagationEntry(
                    server_name=server_name,
                    server_ip=server_ip,
                    resolved_ip=None,
                    response_time=None,
                    status=AuditStatus.ERROR,
                    error=str(exc),
                )

        with ThreadPoolExecutor(max_workers=AuditConfig.MAX_WORKERS) as pool:
            futures = {
                pool.submit(query, name, ip): name
                for name, ip in servers.items()
            }
            for future in as_completed(futures):
                entries.append(future.result())

        return entries
