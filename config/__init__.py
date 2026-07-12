"""
Config module - Centralized configuration for the audit system.
"""

from .settings import AuditConfig
from .dns_servers import DNS_SERVERS, GLOBAL_DNS_SERVERS

__all__ = ["AuditConfig", "DNS_SERVERS", "GLOBAL_DNS_SERVERS"]
