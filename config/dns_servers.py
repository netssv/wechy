#!/usr/bin/env python3
"""
DNS server catalogues used by the DNS agentic skill.

Extracted from the hardcoded dicts in the original WebAuditor class
so they can be extended without touching skill code.
"""

# Quick-access primary servers (used for simple resolution)
DNS_SERVERS = {
    "Google Primary": "8.8.8.8",
    "Google Secondary": "8.8.4.4",
    "Cloudflare Primary": "1.1.1.1",
    "Cloudflare Secondary": "1.0.0.1",
    "Quad9": "9.9.9.9",
    "OpenDNS": "208.67.222.222",
}

# Full global catalogue (used for propagation checks)
GLOBAL_DNS_SERVERS = {
    "Google Primary 🇺🇸": "8.8.8.8",
    "Google Secondary 🇺🇸": "8.8.4.4",
    "Cloudflare Primary 🌍": "1.1.1.1",
    "Cloudflare Secondary 🌍": "1.0.0.1",
    "Quad9 Primary 🇺🇸": "9.9.9.9",
    "Quad9 Secondary 🇨🇭": "149.112.112.112",
    "OpenDNS Primary 🇺🇸": "208.67.222.222",
    "OpenDNS Secondary 🇺🇸": "208.67.220.220",
    "Level3 Primary 🇺🇸": "4.2.2.1",
    "Level3 Secondary 🇺🇸": "4.2.2.2",
    "Yandex Primary 🇷🇺": "77.88.8.8",
    "Yandex Secondary 🇷🇺": "77.88.8.1",
    "Baidu Primary 🇨🇳": "180.76.76.76",
    "ComodoSecure 🇺🇸": "8.26.56.26",
    "CleanBrowsing 🇺🇸": "185.228.168.9",
    "AdGuard DNS 🌍": "94.140.14.14",
}
