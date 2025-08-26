#!/usr/bin/env python3
"""
Enhanced Web Audit Tool - Demo Script
Demonstrates the core functionality without Streamlit interface
"""

from streamlit_web_audit import WebAuditor
import json
import time

def demo_audit(domain):
    """Run a demo audit and display results"""
    print(f"🔍 Enhanced Web Audit Tool - Demo")
    print(f"=" * 50)
    print(f"🎯 Target: {domain}")
    print(f"📅 Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Initialize auditor
    auditor = WebAuditor()
    
    # Extract domain and create URL
    clean_domain = auditor.extract_domain(domain)
    if not domain.startswith(('http://', 'https://')):
        full_url = 'https://' + domain
    else:
        full_url = domain
    
    results = {}
    
    # Step 1: Domain Resolution
    print("🔍 Step 1: Domain Resolution")
    print("-" * 30)
    ip_address = auditor.resolve_domain(clean_domain)
    if ip_address:
        print(f"✅ Domain resolved: {clean_domain} → {ip_address}")
        results['domain_resolution'] = {'domain': clean_domain, 'ip': ip_address, 'status': 'success'}
    else:
        print(f"❌ Failed to resolve domain: {clean_domain}")
        results['domain_resolution'] = {'domain': clean_domain, 'ip': None, 'status': 'failed'}
    print()
    
    # Step 2: Connectivity Check
    print("🌐 Step 2: Connectivity Check")
    print("-" * 30)
    connectivity = auditor.check_connectivity(full_url)
    if connectivity['accessible']:
        print(f"✅ Website is accessible")
        print(f"   Status Code: {connectivity['status_code']}")
        print(f"   Response Time: {connectivity['response_time']:.3f}s")
        if connectivity['redirected']:
            print(f"   Redirected to: {connectivity['final_url']}")
    else:
        print(f"❌ Website is not accessible")
        print(f"   Error: {connectivity.get('error', 'Unknown error')}")
    results['connectivity'] = connectivity
    print()
    
    # Step 3: SSL Certificate Analysis
    if full_url.startswith('https://'):
        print("🔒 Step 3: SSL Certificate Analysis")
        print("-" * 35)
        ssl_info = auditor.get_ssl_info(clean_domain)
        if ssl_info['valid']:
            print(f"✅ SSL Certificate is valid")
            print(f"   Issuer: {ssl_info['issuer'].get('organizationName', 'Unknown')}")
            print(f"   Subject: {ssl_info['subject'].get('commonName', 'Unknown')}")
            print(f"   Valid until: {ssl_info['not_after'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Days until expiry: {ssl_info['days_until_expiry']}")
            
            if ssl_info['days_until_expiry'] < 30:
                print(f"   🚨 WARNING: Certificate expires soon!")
            elif ssl_info['days_until_expiry'] < 90:
                print(f"   ⚠️  NOTICE: Certificate expires in less than 90 days")
            else:
                print(f"   ✅ Certificate has good validity period")
        else:
            print(f"❌ SSL Certificate error: {ssl_info['error']}")
        results['ssl'] = ssl_info
        print()
    
    # Step 4: DNS Records
    print("📋 Step 4: DNS Records Analysis")
    print("-" * 32)
    dns_records = auditor.get_dns_records(clean_domain)
    for record_type, records in dns_records.items():
        if records:
            print(f"   {record_type} Records: {len(records)} found")
            for record in records[:3]:  # Show first 3 records
                print(f"     • {record}")
            if len(records) > 3:
                print(f"     ... and {len(records) - 3} more")
    results['dns_records'] = dns_records
    print()
    
    # Step 5: DNS Propagation Check
    print("🌍 Step 5: DNS Propagation Check")
    print("-" * 33)
    dns_propagation = auditor.check_dns_propagation(clean_domain)
    
    successful_servers = 0
    unique_ips = set()
    
    for server_name, result in dns_propagation.items():
        if result['status'] == 'success' and result['result']:
            successful_servers += 1
            unique_ips.add(result['result'])
            print(f"   ✅ {server_name}: {result['result']} ({result['response_time']:.3f}s)")
        else:
            print(f"   ❌ {server_name}: Failed")
    
    print(f"\n   📊 Summary:")
    print(f"   • Total servers tested: {len(dns_propagation)}")
    print(f"   • Successful responses: {successful_servers}")
    print(f"   • Unique IP addresses: {len(unique_ips)}")
    
    if len(unique_ips) > 1:
        print(f"   ⚠️  DNS propagation inconsistent - multiple IPs found")
        print(f"   💡 This may be normal for load-balanced or CDN-hosted sites")
    else:
        print(f"   ✅ DNS propagation is consistent")
    
    results['dns_propagation'] = dns_propagation
    print()
    
    # Step 6: Performance Analysis
    print("⚡ Step 6: Performance Analysis")
    print("-" * 31)
    performance = auditor.analyze_performance(full_url)
    if 'error' not in performance:
        print(f"   Response Time: {performance['response_time']:.3f}s")
        print(f"   Status Code: {performance['status_code']}")
        print(f"   Content Size: {performance['content_length']:,} bytes")
        print(f"   Web Server: {performance['server']}")
        
        # Performance rating
        rt = performance['response_time']
        if rt < 1.0:
            print(f"   ✅ Performance Rating: Excellent")
        elif rt < 3.0:
            print(f"   ⚠️  Performance Rating: Good")
        else:
            print(f"   ❌ Performance Rating: Needs Improvement")
        
        # Optimization checks
        print(f"\n   🔧 Optimization:")
        if performance['compression_enabled']:
            print(f"   ✅ Compression: Enabled")
        else:
            print(f"   ❌ Compression: Not enabled")
        
        if performance['cache_control']:
            print(f"   ✅ Cache-Control: {performance['cache_control']}")
        else:
            print(f"   ⚠️  Cache-Control: Not set")
        
        # Security headers
        security_headers = performance['security_headers']
        present_headers = sum(security_headers.values())
        total_headers = len(security_headers)
        security_score = (present_headers / total_headers) * 100
        
        print(f"\n   🛡️  Security Headers: {present_headers}/{total_headers} ({security_score:.0f}%)")
        for header, present in security_headers.items():
            status = "✅" if present else "❌"
            print(f"   {status} {header}")
    else:
        print(f"   ❌ Performance analysis failed: {performance['error']}")
    
    results['performance'] = performance
    print()
    
    # Summary
    print("📋 Audit Summary")
    print("=" * 20)
    
    summary_items = []
    if results['domain_resolution']['status'] == 'success':
        summary_items.append("✅ Domain resolution")
    else:
        summary_items.append("❌ Domain resolution")
    
    if results['connectivity']['accessible']:
        summary_items.append("✅ Website accessibility")
    else:
        summary_items.append("❌ Website accessibility")
    
    if 'ssl' in results and results['ssl']['valid']:
        summary_items.append("✅ SSL certificate")
    elif full_url.startswith('https://'):
        summary_items.append("❌ SSL certificate")
    
    if 'performance' in results and 'response_time' in results['performance']:
        rt = results['performance']['response_time']
        if rt < 1.0:
            summary_items.append("✅ Performance")
        elif rt < 3.0:
            summary_items.append("⚠️ Performance")
        else:
            summary_items.append("❌ Performance")
    
    for item in summary_items:
        print(f"   {item}")
    
    print(f"\n🕒 Audit completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 Full results available in JSON format")
    
    return results

def main():
    """Main demo function"""
    import sys
    
    if len(sys.argv) > 1:
        domain = sys.argv[1]
    else:
        domain = input("🌐 Enter a domain to audit (e.g., github.com): ").strip()
    
    if not domain:
        print("❌ No domain provided")
        return
    
    try:
        results = demo_audit(domain)
        
        # Offer to save results
        save_results = input("\n💾 Save results to JSON file? (y/n): ").strip().lower()
        if save_results in ['y', 'yes']:
            filename = f"audit_results_{domain.replace('.', '_')}_{int(time.time())}.json"
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"✅ Results saved to: {filename}")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Audit interrupted by user")
    except Exception as e:
        print(f"\n❌ Audit failed: {str(e)}")

if __name__ == "__main__":
    main()
