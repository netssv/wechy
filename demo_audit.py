#!/usr/bin/env python3
"""
Enhanced Web Audit Tool - Demo Command Line Runner
Runs the new modular, agentic architecture from the console.
"""

import os
import sys
import argparse
from datetime import datetime
from config.settings import AuditConfig
from models.audit_result import AuditReport
from skills.skill_registry import SkillRegistry
from agents.llm_client import LLMClient
from agents.audit_agent import AuditAgent

# Import skills to register them
import skills.dns_skill
import skills.ssl_skill
import skills.performance_skill
import skills.security_skill
import skills.whois_skill
import skills.tech_detection_skill


def run_demo(target: str, mode: str):
    print("=" * 60)
    print(f"🤖 Starting AI Agentic Web Audit on: {target}")
    print(f"⚙️  Mode: {mode}")
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Resolve LLM Credentials
    api_key = os.getenv("LLM_API_KEY", "")
    if not api_key:
        print("⚠️  Warning: LLM_API_KEY environment variable not set.")
        print("The agent will attempt to resolve/reason locally, or run may fail if using Google/OpenAI.")

    # Create LLM client and Agent
    client = LLMClient.create(
        provider=AuditConfig.LLM_PROVIDER,
        model=AuditConfig.LLM_MODEL,
        api_key=api_key
    )
    
    agent = AuditAgent(llm_client=client)

    print("🧠 AI Agent orchestrating skills...")
    report: AuditReport = agent.run(target, mode=mode)

    print("\n" + "=" * 60)
    print("📊 AUDIT RESULTS SUMMARY")
    print("=" * 60)
    print(f"Target URL: {report.url}")
    print(f"Resolved Domain: {report.domain}")
    print(f"Execution Time: {report.total_execution_time:.2f} seconds")
    print(f"Skills Executed: {', '.join(report.skills_executed)}")
    if report.health_score is not None:
        print(f"AI Health Score: {report.health_score}/100")
    print("=" * 60)

    if report.dns:
        print(f"🌐 DNS: Resolved to {report.dns.ip_address} (Consistency: {report.dns.is_consistent})")
    if report.ssl:
        print(f"🔒 SSL: Valid={report.ssl.valid}, Days left={report.ssl.days_until_expiry}")
    if report.performance:
        print(f"⚡ Performance: HTTP {report.performance.status_code}, Response time={report.performance.response_time:.3f}s")
    if report.security:
        print(f"🛡️  Security Headers Score: {report.security.score:.0f}%")
    if report.tech_detection:
        print(f"🔧 Tech Detected: {', '.join(report.tech_detection.technologies)}")

    print("\n" + "=" * 60)
    print("🧠 AI EXECUTIVE ANALYSIS")
    print("=" * 60)
    if report.ai_analysis:
        print(report.ai_analysis)
    else:
        print("No analysis returned.")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Run the agentic web auditor.")
    parser.add_argument("target", help="Website URL or domain to audit")
    parser.add_argument("--mode", choices=["quick", "comprehensive"], default="comprehensive", help="Audit mode")
    args = parser.parse_args()

    run_demo(args.target, args.mode)


if __name__ == "__main__":
    main()
