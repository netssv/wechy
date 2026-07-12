#!/usr/bin/env python3
"""
Main entrypoint for the Streamlit Web Audit Application.
"""

import os
import streamlit as st
from config.settings import AuditConfig
from models.audit_result import AuditReport
from skills.skill_registry import SkillRegistry
from agents.llm_client import LLMClient
from agents.audit_agent import AuditAgent
from ui.components import (
    render_metric_cards,
    render_dns_tab,
    render_ssl_tab,
    render_performance_tab,
    render_security_tab,
    render_whois_tab,
)

# Page Configuration
st.set_page_config(
    page_title="AI-Agentic Web Audit Tool",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Import all skills to trigger registration decorators
import skills.dns_skill
import skills.ssl_skill
import skills.performance_skill
import skills.security_skill
import skills.whois_skill
import skills.tech_detection_skill


def main():
    st.markdown("""
    <div class="main-header">
        <h1>🔍 AI-Agentic Web Audit Tool</h1>
        <p>Dynamic Multi-Agent Web Inspection powered by Autonomous Skills</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar Configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        url_input = st.text_input(
            "🌐 Target Website URL",
            placeholder="example.com or https://example.com"
        )

        audit_mode = st.selectbox(
            "🤖 Audit Mode",
            ["comprehensive", "quick"]
        )

        st.markdown("---")
        st.subheader("🔑 AI Agent Keys")
        # Let user provide key or fallback to env
        api_key = st.text_input("LLM API Key (Optional)", type="password", value=os.getenv("LLM_API_KEY", ""))

        st.markdown("---")
        st.subheader("🧩 Registered Agentic Skills")
        for skill in SkillRegistry.get_all_skills():
            st.markdown(f"- **{skill.display_name}** (`{skill.name}`): {skill.description[:60]}...")

        start_audit = st.button("🚀 Run AI Audit", type="primary", use_container_width=True)

    if start_audit and url_input:
        # Build Agent Setup
        key_to_use = api_key if api_key else os.getenv("LLM_API_KEY", "")
        
        # Configure model
        client = LLMClient.create(
            provider=AuditConfig.LLM_PROVIDER,
            model=AuditConfig.LLM_MODEL,
            api_key=key_to_use
        )
        
        agent = AuditAgent(llm_client=client)

        with st.spinner("🧠 AI Agent thinking and orchestrating skills..."):
            report: AuditReport = agent.run(url_input, mode=audit_mode)

        # Overview Metrics
        st.header("📊 Audit Overview")
        render_metric_cards(report)

        st.markdown("---")

        # Tabs for details
        tab_ai, tab_dns, tab_ssl, tab_perf, tab_security, tab_whois = st.tabs([
            "🧠 AI Executive Analysis",
            "🌐 DNS Analysis",
            "🔒 SSL Certificate",
            "⚡ Performance",
            "🛡️ HTTP Security",
            "📄 Domain Info"
        ])

        with tab_ai:
            st.subheader("📝 Agent Executive Report")
            if report.ai_analysis:
                st.write(report.ai_analysis)
            else:
                st.warning("Agent did not return analysis content.")

            if report.recommendations:
                st.subheader("💡 Actionable Recommendations")
                for rec in report.recommendations:
                    st.write(rec)

        with tab_dns:
            render_dns_tab(report)

        with tab_ssl:
            render_ssl_tab(report)

        with tab_perf:
            render_performance_tab(report)

        with tab_security:
            render_security_tab(report)

        with tab_whois:
            render_whois_tab(report)

    elif start_audit and not url_input:
        st.error("Please enter a valid target URL or domain name.")


if __name__ == "__main__":
    main()
