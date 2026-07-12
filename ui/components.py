#!/usr/bin/env python3
"""
UI Components module for the Streamlit interface.
Defines layout cards, metadata views, and tables.
"""

import streamlit as st
import pandas as pd
from models.audit_result import AuditReport, AuditStatus


def render_metric_cards(report: AuditReport):
    """Renders the top summary metric cards."""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if report.dns and report.dns.ip_address:
            st.metric("🌐 Domain Status", "✅ Resolved", report.dns.ip_address)
        else:
            st.metric("🌐 Domain Status", "❌ Failed", "No IP")

    with col2:
        if report.performance and report.performance.status_code:
            st.metric("🔗 Connectivity", "✅ Online", f"HTTP {report.performance.status_code}")
        else:
            st.metric("🔗 Connectivity", "❌ Offline", "Unreachable")

    with col3:
        if report.ssl and report.ssl.valid:
            days = report.ssl.days_until_expiry
            st.metric("🔒 SSL Certificate", "✅ Valid", f"{days} days left")
        elif report.ssl:
            st.metric("🔒 SSL Certificate", "❌ Invalid", "Error")
        else:
            st.metric("🔒 SSL Certificate", "ℹ️ HTTP Only", "No SSL")

    with col4:
        if report.health_score is not None:
            score = report.health_score
            verdict = "🟢 Good" if score >= 80 else "🟡 Warning" if score >= 50 else "🔴 Critical"
            st.metric("🛡️ AI Health Score", f"{score}/100", verdict)
        else:
            st.metric("🛡️ AI Health Score", "N/A", "Awaiting AI")


def render_dns_tab(report: AuditReport):
    """Renders the DNS Analysis and Propagation UI."""
    if not report.dns:
        st.info("DNS information not available for this audit.")
        return

    st.subheader("DNS Records")
    dns_data = []
    for record_type, records in report.dns.records.items():
        for record in records:
            dns_data.append({
                'Type': record_type,
                'Value': record
            })

    if dns_data:
        df_dns = pd.DataFrame(dns_data)
        st.dataframe(df_dns, use_container_width=True)
    else:
        st.write("No DNS records found.")

    st.subheader("🌍 Global DNS Propagation")
    propagation_data = []
    for entry in report.dns.propagation:
        propagation_data.append({
            'DNS Server': entry.server_name,
            'IP Address': entry.resolved_ip or 'Failed',
            'Response Time': f"{entry.response_time:.3f}s" if entry.response_time else 'N/A',
            'Status': '✅ Success' if entry.status == AuditStatus.SUCCESS else '❌ Error'
        })

    if propagation_data:
        df_prop = pd.DataFrame(propagation_data)
        st.dataframe(df_prop, use_container_width=True)

        if report.dns.is_consistent:
            st.success("✅ DNS propagation consistent across all servers.")
        else:
            st.warning(f"⚠️ DNS propagation inconsistent - {report.dns.unique_ips} different IP addresses found.")


def render_ssl_tab(report: AuditReport):
    """Renders SSL details."""
    if not report.ssl:
        st.info("SSL Certificate analysis was skipped or failed.")
        return

    if report.ssl.valid:
        st.success("✅ SSL Certificate is valid")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Certificate Details")
            st.write(f"**Subject:** {report.ssl.subject.get('commonName', 'N/A') if report.ssl.subject else 'N/A'}")
            st.write(f"**Issuer:** {report.ssl.issuer.get('organizationName', 'N/A') if report.ssl.issuer else 'N/A'}")
            st.write(f"**Valid From:** {report.ssl.not_before.strftime('%Y-%m-%d %H:%M:%S') if report.ssl.not_before else 'N/A'}")
            st.write(f"**Valid Until:** {report.ssl.not_after.strftime('%Y-%m-%d %H:%M:%S') if report.ssl.not_after else 'N/A'}")
            st.write(f"**Days Until Expiry:** {report.ssl.days_until_expiry}")
        with col2:
            st.subheader("Certificate Status")
            days = report.ssl.days_until_expiry
            if days < 30:
                st.error(f"🚨 Certificate expires in {days} days!")
            elif days < 90:
                st.warning(f"⚠️ Certificate expires in {days} days")
            else:
                st.success(f"✅ Certificate valid for {days} days")

            if report.ssl.subject_alt_names:
                st.write("**Subject Alternative Names (SANs):**")
                for san in report.ssl.subject_alt_names[:10]:
                    st.write(f"• {san}")
                if len(report.ssl.subject_alt_names) > 10:
                    st.write(f"... and {len(report.ssl.subject_alt_names) - 10} more.")
    else:
        st.error(f"❌ SSL Certificate Error: {report.ssl.error}")


def render_performance_tab(report: AuditReport):
    """Renders Performance details."""
    if not report.performance:
        st.info("Performance analysis was skipped or failed.")
        return

    if report.performance.error:
        st.error(f"❌ Performance analysis failed: {report.performance.error}")
        return

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Performance Metrics")
        st.metric("Response Time", f"{report.performance.response_time:.3f}s")
        st.metric("Status Code", report.performance.status_code)
        st.metric("Content Size", f"{report.performance.content_length:,} bytes" if report.performance.content_length else "Unknown")
        st.metric("Web Server", report.performance.server)
    with col2:
        st.subheader("Optimizations")
        if report.performance.compression_enabled:
            st.success("✅ Compression enabled")
        else:
            st.error("❌ Compression not enabled")

        if report.performance.cache_control:
            st.success(f"✅ Cache-Control: {report.performance.cache_control}")
        else:
            st.warning("⚠️ No Cache-Control header found")

        if report.performance.etag:
            st.success("✅ ETag header present")
        else:
            st.warning("⚠️ No ETag header found")


def render_security_tab(report: AuditReport):
    """Renders Security headers."""
    if not report.security:
        st.info("Security analysis was skipped or failed.")
        return

    st.subheader("🛡️ HTTP Security Headers")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("Security Score", f"{report.security.score:.0f}%")
    with col2:
        for header, present in report.security.headers_present.items():
            if present:
                st.success(f"✅ {header}")
            else:
                st.error(f"❌ {header}")

    st.subheader("🔧 Recommendations")
    if report.security.missing_headers:
        for header in report.security.missing_headers:
            st.write(f"• **{header}** is missing. Configure this header to mitigate potential security vulnerabilities.")
    else:
        st.success("🎉 Excellent! All security headers analyzed are present.")


def render_whois_tab(report: AuditReport):
    """Renders WHOIS and Tech Detection details."""
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📄 Domain Information (WHOIS)")
        if report.whois:
            if report.whois.error:
                st.error(f"WHOIS lookup failed: {report.whois.error}")
            else:
                st.write(f"**Registrar:** {report.whois.registrar or 'N/A'}")
                st.write(f"**Creation Date:** {report.whois.creation_date or 'N/A'}")
                st.write(f"**Expiration Date:** {report.whois.expiration_date or 'N/A'}")
                st.write(f"**Country:** {report.whois.country or 'N/A'}")
                if report.whois.name_servers:
                    st.write(f"**Name Servers:** {', '.join(report.whois.name_servers[:3])}")
        else:
            st.info("WHOIS information not checked.")

    with col2:
        st.subheader("🔧 Tech Stack Fingerprint")
        if report.tech_detection:
            st.write(f"**Web Server:** {report.tech_detection.server or 'Unknown'}")
            st.write(f"**Powered By:** {report.tech_detection.powered_by or 'Unknown'}")
            if report.tech_detection.technologies:
                st.write("**Detected Technologies:**")
                for tech in report.tech_detection.technologies:
                    st.write(f"• {tech}")
            else:
                st.info("No CMS or specific library technologies detected in raw content.")
        else:
            st.info("Technology fingerprinting not run.")
