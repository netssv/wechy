#!/usr/bin/env python3
"""
Enhanced Web Audit Tool - Streamlit Version
Author: netss - Enhanced by Web Analyst
GitHub: https://github.com/netssv
Description: A comprehensive web audit tool with Streamlit interface
"""

import streamlit as st
import requests
import socket
import ssl
import dns.resolver
import subprocess
import time
import json
import re
import whois
from urllib.parse import urlparse
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Enhanced Web Audit Tool",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
    }
    .success-metric {
        border-left-color: #28a745;
    }
    .warning-metric {
        border-left-color: #ffc107;
    }
    .error-metric {
        border-left-color: #dc3545;
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

class WebAuditor:
    def __init__(self):
        self.dns_servers = {
            'Google Primary': '8.8.8.8',
            'Google Secondary': '8.8.4.4',
            'Cloudflare Primary': '1.1.1.1',
            'Cloudflare Secondary': '1.0.0.1',
            'Quad9': '9.9.9.9',
            'OpenDNS': '208.67.222.222'
        }
        
        self.global_dns_servers = {
            'Google Primary 🇺🇸': '8.8.8.8',
            'Google Secondary 🇺🇸': '8.8.4.4',
            'Cloudflare Primary 🌍': '1.1.1.1',
            'Cloudflare Secondary 🌍': '1.0.0.1',
            'Quad9 Primary 🇺🇸': '9.9.9.9',
            'Quad9 Secondary 🇨🇭': '149.112.112.112',
            'OpenDNS Primary 🇺🇸': '208.67.222.222',
            'OpenDNS Secondary 🇺🇸': '208.67.220.220',
            'Level3 Primary 🇺🇸': '4.2.2.1',
            'Level3 Secondary 🇺🇸': '4.2.2.2',
            'Yandex Primary 🇷🇺': '77.88.8.8',
            'Yandex Secondary 🇷🇺': '77.88.8.1',
            'Baidu Primary 🇨🇳': '180.76.76.76',
            'ComodoSecure 🇺🇸': '8.26.56.26',
            'CleanBrowsing 🇺🇸': '185.228.168.9',
            'AdGuard DNS 🌍': '94.140.14.14'
        }
        
    def extract_domain(self, url):
        """Extract domain from URL"""
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return urlparse(url).netloc
    
    def resolve_domain(self, domain):
        """Resolve domain to IP address"""
        try:
            result = socket.gethostbyname(domain)
            return result
        except socket.gaierror:
            return None
    
    def check_connectivity(self, url):
        """Check if website is accessible"""
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            response = requests.get(url, timeout=10, allow_redirects=True)
            return {
                'accessible': True,
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds(),
                'final_url': response.url,
                'redirected': url != response.url
            }
        except Exception as e:
            return {
                'accessible': False,
                'error': str(e),
                'status_code': None,
                'response_time': None
            }
    
    def get_ssl_info(self, domain):
        """Get SSL certificate information"""
        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Parse dates
                    not_before = datetime.strptime(cert['notBefore'], '%b %d %H:%M:%S %Y %Z')
                    not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    days_until_expiry = (not_after - datetime.now()).days
                    
                    return {
                        'valid': True,
                        'issuer': dict(x[0] for x in cert['issuer']),
                        'subject': dict(x[0] for x in cert['subject']),
                        'not_before': not_before,
                        'not_after': not_after,
                        'days_until_expiry': days_until_expiry,
                        'serial_number': cert['serialNumber'],
                        'version': cert['version'],
                        'subject_alt_names': [x[1] for x in cert.get('subjectAltName', [])]
                    }
        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }
    
    def check_dns_propagation(self, domain):
        """Check DNS propagation across global servers"""
        results = {}
        
        def query_dns_server(server_name, server_ip):
            try:
                resolver = dns.resolver.Resolver()
                resolver.nameservers = [server_ip]
                resolver.timeout = 5
                resolver.lifetime = 5
                
                start_time = time.time()
                answer = resolver.resolve(domain, 'A')
                response_time = time.time() - start_time
                
                return {
                    'server': server_name,
                    'ip': server_ip,
                    'result': str(answer[0]),
                    'response_time': response_time,
                    'status': 'success'
                }
            except Exception as e:
                return {
                    'server': server_name,
                    'ip': server_ip,
                    'result': None,
                    'response_time': None,
                    'status': 'error',
                    'error': str(e)
                }
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {
                executor.submit(query_dns_server, name, ip): name 
                for name, ip in self.global_dns_servers.items()
            }
            
            for future in as_completed(futures):
                result = future.result()
                results[result['server']] = result
        
        return results
    
    def get_dns_records(self, domain):
        """Get various DNS records for the domain"""
        records = {}
        record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA']
        
        for record_type in record_types:
            try:
                resolver = dns.resolver.Resolver()
                answers = resolver.resolve(domain, record_type)
                records[record_type] = [str(answer) for answer in answers]
            except Exception:
                records[record_type] = []
        
        return records
    
    def analyze_performance(self, url):
        """Analyze website performance"""
        try:
            start_time = time.time()
            response = requests.get(url, timeout=30)
            total_time = time.time() - start_time
            
            # Calculate various metrics
            headers = dict(response.headers)
            content_length = len(response.content)
            
            # Check for compression
            compression = 'gzip' in headers.get('content-encoding', '').lower()
            
            # Check for caching headers
            cache_control = headers.get('cache-control', '')
            etag = headers.get('etag', '')
            last_modified = headers.get('last-modified', '')
            
            # Security headers check
            security_headers = {
                'Strict-Transport-Security': 'strict-transport-security' in headers,
                'X-Content-Type-Options': 'x-content-type-options' in headers,
                'X-Frame-Options': 'x-frame-options' in headers,
                'X-XSS-Protection': 'x-xss-protection' in headers,
                'Content-Security-Policy': 'content-security-policy' in headers,
                'Referrer-Policy': 'referrer-policy' in headers
            }
            
            return {
                'response_time': total_time,
                'status_code': response.status_code,
                'content_length': content_length,
                'compression_enabled': compression,
                'cache_control': cache_control,
                'etag': bool(etag),
                'last_modified': bool(last_modified),
                'security_headers': security_headers,
                'headers': headers,
                'server': headers.get('server', 'Unknown')
            }
        except Exception as e:
            return {
                'error': str(e),
                'response_time': None
            }
    
    def get_whois_info(self, domain):
        """Get WHOIS information for the domain"""
        try:
            w = whois.whois(domain)
            return {
                'registrar': w.registrar,
                'creation_date': w.creation_date,
                'expiration_date': w.expiration_date,
                'name_servers': w.name_servers,
                'status': w.status,
                'country': getattr(w, 'country', None)
            }
        except Exception as e:
            return {
                'error': str(e)
            }
    
    def detect_technologies(self, url, headers, content):
        """Detect web technologies"""
        technologies = []
        
        # Server detection
        server = headers.get('server', '').lower()
        if 'nginx' in server:
            technologies.append('Nginx')
        elif 'apache' in server:
            technologies.append('Apache')
        elif 'cloudflare' in server:
            technologies.append('Cloudflare')
        elif 'microsoft-iis' in server:
            technologies.append('Microsoft IIS')
        
        # Framework detection
        if 'x-powered-by' in headers:
            powered_by = headers['x-powered-by'].lower()
            if 'php' in powered_by:
                technologies.append('PHP')
            elif 'asp.net' in powered_by:
                technologies.append('ASP.NET')
        
        # Content-based detection
        content_lower = content.lower()
        if 'wordpress' in content_lower:
            technologies.append('WordPress')
        elif 'drupal' in content_lower:
            technologies.append('Drupal')
        elif 'joomla' in content_lower:
            technologies.append('Joomla')
        
        # JavaScript frameworks
        if 'react' in content_lower:
            technologies.append('React')
        elif 'vue' in content_lower:
            technologies.append('Vue.js')
        elif 'angular' in content_lower:
            technologies.append('Angular')
        
        return technologies

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🔍 Enhanced Web Audit Tool</h1>
        <p>Comprehensive website analysis with DNS, SSL, performance, and security checks</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("🛠️ Audit Configuration")
        
        # URL input
        url_input = st.text_input(
            "🌐 Website URL or Domain",
            placeholder="example.com or https://example.com",
            help="Enter the website you want to audit"
        )
        
        # Audit mode
        audit_mode = st.selectbox(
            "⚙️ Audit Mode",
            ["Quick Audit", "Comprehensive Audit"],
            help="Quick: Essential checks only. Comprehensive: Full analysis"
        )
        
        # Advanced options
        with st.expander("🔧 Advanced Options"):
            include_dns_propagation = st.checkbox("Check DNS Propagation", value=True)
            include_ssl_analysis = st.checkbox("SSL Certificate Analysis", value=True)
            include_performance = st.checkbox("Performance Analysis", value=True)
            include_security = st.checkbox("Security Headers Check", value=True)
            include_whois = st.checkbox("WHOIS Information", value=False)
        
        # Start audit button
        start_audit = st.button("🚀 Start Audit", type="primary", use_container_width=True)
    
    # Main content area
    if start_audit and url_input:
        # Initialize auditor
        auditor = WebAuditor()
        
        # Extract domain
        domain = auditor.extract_domain(url_input)
        if not url_input.startswith(('http://', 'https://')):
            full_url = 'https://' + url_input
        else:
            full_url = url_input
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Results container
        results = {}
        
        # Step 1: Domain Resolution
        status_text.text("🔍 Resolving domain...")
        progress_bar.progress(10)
        
        ip_address = auditor.resolve_domain(domain)
        results['domain_resolution'] = {
            'domain': domain,
            'ip_address': ip_address,
            'resolved': ip_address is not None
        }
        
        # Step 2: Connectivity Check
        status_text.text("🌐 Checking website connectivity...")
        progress_bar.progress(20)
        
        connectivity = auditor.check_connectivity(full_url)
        results['connectivity'] = connectivity
        
        # Step 3: SSL Analysis
        if include_ssl_analysis and full_url.startswith('https://'):
            status_text.text("🔒 Analyzing SSL certificate...")
            progress_bar.progress(30)
            
            ssl_info = auditor.get_ssl_info(domain)
            results['ssl'] = ssl_info
        
        # Step 4: DNS Records
        status_text.text("📋 Retrieving DNS records...")
        progress_bar.progress(40)
        
        dns_records = auditor.get_dns_records(domain)
        results['dns_records'] = dns_records
        
        # Step 5: DNS Propagation
        if include_dns_propagation:
            status_text.text("🌍 Checking DNS propagation...")
            progress_bar.progress(60)
            
            dns_propagation = auditor.check_dns_propagation(domain)
            results['dns_propagation'] = dns_propagation
        
        # Step 6: Performance Analysis
        if include_performance:
            status_text.text("⚡ Analyzing performance...")
            progress_bar.progress(75)
            
            performance = auditor.analyze_performance(full_url)
            results['performance'] = performance
        
        # Step 7: WHOIS Information
        if include_whois:
            status_text.text("📄 Retrieving WHOIS information...")
            progress_bar.progress(85)
            
            whois_info = auditor.get_whois_info(domain)
            results['whois'] = whois_info
        
        # Complete
        status_text.text("✅ Audit completed!")
        progress_bar.progress(100)
        
        # Display Results
        st.markdown("---")
        st.header("📊 Audit Results")
        
        # Overview metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if results['domain_resolution']['resolved']:
                st.metric("🌐 Domain Status", "✅ Resolved", results['domain_resolution']['ip_address'])
            else:
                st.metric("🌐 Domain Status", "❌ Failed", "No IP")
        
        with col2:
            if results['connectivity']['accessible']:
                st.metric("🔗 Connectivity", "✅ Online", f"{results['connectivity']['status_code']}")
            else:
                st.metric("🔗 Connectivity", "❌ Offline", "Error")
        
        with col3:
            if 'ssl' in results and results['ssl']['valid']:
                days = results['ssl']['days_until_expiry']
                st.metric("🔒 SSL Certificate", "✅ Valid", f"{days} days left")
            elif full_url.startswith('https://'):
                st.metric("🔒 SSL Certificate", "❌ Invalid", "Check needed")
            else:
                st.metric("🔒 SSL Certificate", "ℹ️ HTTP", "No SSL")
        
        with col4:
            if 'performance' in results and 'response_time' in results['performance']:
                response_time = results['performance']['response_time']
                st.metric("⚡ Response Time", f"{response_time:.3f}s", 
                         "🟢 Good" if response_time < 1.0 else "🟡 Slow" if response_time < 3.0 else "🔴 Very Slow")
            else:
                st.metric("⚡ Response Time", "❌ Failed", "No data")
        
        # Detailed results in tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["🌐 DNS Analysis", "🔒 SSL Certificate", "⚡ Performance", "🛡️ Security", "📄 Domain Info"])
        
        with tab1:
            st.subheader("DNS Records")
            
            # DNS Records Table
            dns_data = []
            for record_type, records in results['dns_records'].items():
                for record in records:
                    dns_data.append({
                        'Type': record_type,
                        'Value': record
                    })
            
            if dns_data:
                df_dns = pd.DataFrame(dns_data)
                st.dataframe(df_dns, use_container_width=True)
            
            # DNS Propagation
            if 'dns_propagation' in results:
                st.subheader("🌍 Global DNS Propagation")
                
                propagation_data = []
                unique_ips = set()
                
                for server_name, result in results['dns_propagation'].items():
                    if result['status'] == 'success' and result['result']:
                        unique_ips.add(result['result'])
                        propagation_data.append({
                            'DNS Server': server_name,
                            'IP Address': result['result'],
                            'Response Time': f"{result['response_time']:.3f}s" if result['response_time'] else 'N/A',
                            'Status': '✅ Success'
                        })
                    else:
                        propagation_data.append({
                            'DNS Server': server_name,
                            'IP Address': 'Failed',
                            'Response Time': 'N/A',
                            'Status': '❌ Error'
                        })
                
                df_propagation = pd.DataFrame(propagation_data)
                st.dataframe(df_propagation, use_container_width=True)
                
                # Propagation summary
                total_servers = len(results['dns_propagation'])
                successful_servers = len([r for r in results['dns_propagation'].values() if r['status'] == 'success'])
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Servers", total_servers)
                with col2:
                    st.metric("Responding Servers", successful_servers)
                with col3:
                    st.metric("Unique IPs", len(unique_ips))
                
                if len(unique_ips) > 1:
                    st.warning(f"⚠️ DNS propagation inconsistent - {len(unique_ips)} different IP addresses found")
                else:
                    st.success("✅ DNS propagation consistent across all servers")
        
        with tab2:
            if 'ssl' in results:
                ssl_data = results['ssl']
                
                if ssl_data['valid']:
                    st.success("✅ SSL Certificate is valid")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Certificate Details")
                        st.write(f"**Subject:** {ssl_data['subject'].get('commonName', 'N/A')}")
                        st.write(f"**Issuer:** {ssl_data['issuer'].get('organizationName', 'N/A')}")
                        st.write(f"**Valid From:** {ssl_data['not_before'].strftime('%Y-%m-%d %H:%M:%S')}")
                        st.write(f"**Valid Until:** {ssl_data['not_after'].strftime('%Y-%m-%d %H:%M:%S')}")
                        st.write(f"**Days Until Expiry:** {ssl_data['days_until_expiry']}")
                    
                    with col2:
                        st.subheader("Certificate Status")
                        
                        # Expiry warning
                        if ssl_data['days_until_expiry'] < 30:
                            st.error(f"🚨 Certificate expires in {ssl_data['days_until_expiry']} days!")
                        elif ssl_data['days_until_expiry'] < 90:
                            st.warning(f"⚠️ Certificate expires in {ssl_data['days_until_expiry']} days")
                        else:
                            st.success(f"✅ Certificate valid for {ssl_data['days_until_expiry']} days")
                        
                        # Subject Alternative Names
                        if ssl_data['subject_alt_names']:
                            st.subheader("Subject Alternative Names")
                            for san in ssl_data['subject_alt_names']:
                                st.write(f"• {san}")
                
                else:
                    st.error(f"❌ SSL Certificate error: {ssl_data['error']}")
            
            elif full_url.startswith('http://'):
                st.info("ℹ️ Website uses HTTP - no SSL certificate")
            else:
                st.warning("⚠️ SSL analysis was disabled")
        
        with tab3:
            if 'performance' in results:
                perf_data = results['performance']
                
                if 'error' not in perf_data:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Performance Metrics")
                        st.metric("Response Time", f"{perf_data['response_time']:.3f}s")
                        st.metric("Status Code", perf_data['status_code'])
                        st.metric("Content Size", f"{perf_data['content_length']:,} bytes")
                        st.metric("Web Server", perf_data['server'])
                    
                    with col2:
                        st.subheader("Optimization")
                        
                        # Compression
                        if perf_data['compression_enabled']:
                            st.success("✅ Compression enabled")
                        else:
                            st.error("❌ Compression not enabled")
                        
                        # Caching
                        if perf_data['cache_control']:
                            st.success(f"✅ Cache-Control: {perf_data['cache_control']}")
                        else:
                            st.warning("⚠️ No Cache-Control header")
                        
                        if perf_data['etag']:
                            st.success("✅ ETag header present")
                        else:
                            st.warning("⚠️ No ETag header")
                    
                    # Response time visualization
                    st.subheader("Response Time Analysis")
                    
                    # Create a simple gauge chart
                    fig = go.Figure(go.Indicator(
                        mode = "gauge+number+delta",
                        value = perf_data['response_time'],
                        domain = {'x': [0, 1], 'y': [0, 1]},
                        title = {'text': "Response Time (seconds)"},
                        delta = {'reference': 1.0},
                        gauge = {
                            'axis': {'range': [None, 5]},
                            'bar': {'color': "darkblue"},
                            'steps': [
                                {'range': [0, 1], 'color': "lightgreen"},
                                {'range': [1, 3], 'color': "yellow"},
                                {'range': [3, 5], 'color': "red"}
                            ],
                            'threshold': {
                                'line': {'color': "red", 'width': 4},
                                'thickness': 0.75,
                                'value': 3.0
                            }
                        }
                    ))
                    
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, use_container_width=True)
                
                else:
                    st.error(f"❌ Performance analysis failed: {perf_data['error']}")
        
        with tab4:
            if 'performance' in results and 'security_headers' in results['performance']:
                st.subheader("🛡️ Security Headers Analysis")
                
                security_headers = results['performance']['security_headers']
                
                # Security score calculation
                total_headers = len(security_headers)
                present_headers = sum(security_headers.values())
                security_score = (present_headers / total_headers) * 100
                
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    # Security score gauge
                    fig = go.Figure(go.Indicator(
                        mode = "gauge+number",
                        value = security_score,
                        domain = {'x': [0, 1], 'y': [0, 1]},
                        title = {'text': "Security Score (%)"},
                        gauge = {
                            'axis': {'range': [None, 100]},
                            'bar': {'color': "darkblue"},
                            'steps': [
                                {'range': [0, 50], 'color': "red"},
                                {'range': [50, 80], 'color': "yellow"},
                                {'range': [80, 100], 'color': "green"}
                            ]
                        }
                    ))
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.subheader("Security Headers Status")
                    
                    for header, present in security_headers.items():
                        if present:
                            st.success(f"✅ {header}")
                        else:
                            st.error(f"❌ {header}")
                
                # Recommendations
                st.subheader("🔧 Security Recommendations")
                
                missing_headers = [header for header, present in security_headers.items() if not present]
                
                if not missing_headers:
                    st.success("🎉 Excellent! All important security headers are present.")
                else:
                    st.warning(f"⚠️ Missing {len(missing_headers)} security headers:")
                    for header in missing_headers:
                        st.write(f"• **{header}**: Helps protect against various attacks")
        
        with tab5:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Domain Information")
                st.write(f"**Domain:** {domain}")
                st.write(f"**IP Address:** {ip_address}")
                
                if results['connectivity']['accessible']:
                    st.write(f"**Final URL:** {results['connectivity']['final_url']}")
                    if results['connectivity']['redirected']:
                        st.info("ℹ️ Website redirects to a different URL")
            
            with col2:
                if 'whois' in results:
                    st.subheader("WHOIS Information")
                    whois_data = results['whois']
                    
                    if 'error' not in whois_data:
                        if whois_data['registrar']:
                            st.write(f"**Registrar:** {whois_data['registrar']}")
                        if whois_data['creation_date']:
                            st.write(f"**Created:** {whois_data['creation_date']}")
                        if whois_data['expiration_date']:
                            st.write(f"**Expires:** {whois_data['expiration_date']}")
                        if whois_data['name_servers']:
                            st.write(f"**Name Servers:** {', '.join(whois_data['name_servers'][:3])}")
                    else:
                        st.error(f"WHOIS lookup failed: {whois_data['error']}")
        
        # Export results
        st.markdown("---")
        st.subheader("📥 Export Results")
        
        if st.button("📋 Copy Results as JSON"):
            json_results = json.dumps(results, indent=2, default=str)
            st.code(json_results, language='json')
        
        # Summary and recommendations
        st.markdown("---")
        st.subheader("📋 Audit Summary")
        
        summary_points = []
        
        if results['domain_resolution']['resolved']:
            summary_points.append("✅ Domain resolves correctly")
        else:
            summary_points.append("❌ Domain resolution failed")
        
        if results['connectivity']['accessible']:
            summary_points.append("✅ Website is accessible")
        else:
            summary_points.append("❌ Website is not accessible")
        
        if 'ssl' in results and results['ssl']['valid']:
            summary_points.append("✅ SSL certificate is valid")
        
        if 'performance' in results and 'response_time' in results['performance']:
            rt = results['performance']['response_time']
            if rt < 1.0:
                summary_points.append("✅ Good response time")
            elif rt < 3.0:
                summary_points.append("⚠️ Moderate response time")
            else:
                summary_points.append("❌ Slow response time")
        
        for point in summary_points:
            st.write(point)
    
    elif start_audit and not url_input:
        st.error("❌ Please enter a URL or domain to audit")
    
    else:
        # Welcome message
        st.info("""
        👋 **Welcome to the Enhanced Web Audit Tool!**
        
        This tool provides comprehensive analysis of websites including:
        
        🔍 **DNS Analysis**: Check DNS records and global propagation
        🔒 **SSL Certificate**: Validate certificates and expiry dates  
        ⚡ **Performance**: Measure response times and optimization
        🛡️ **Security**: Analyze security headers and best practices
        📄 **Domain Info**: WHOIS data and domain information
        
        Enter a website URL in the sidebar to get started!
        """)
        
        # Example domains
        st.subheader("🧪 Try with example domains:")
        
        example_col1, example_col2, example_col3 = st.columns(3)
        
        with example_col1:
            if st.button("Test Google", use_container_width=True):
                st.session_state.example_url = "google.com"
        
        with example_col2:
            if st.button("Test GitHub", use_container_width=True):
                st.session_state.example_url = "github.com"
        
        with example_col3:
            if st.button("Test Cloudflare", use_container_width=True):
                st.session_state.example_url = "cloudflare.com"

if __name__ == "__main__":
    main()
