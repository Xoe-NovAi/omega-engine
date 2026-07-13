"""SovereignProxyPool — domain-affinity proxy rotation with health monitoring.

To the target, you must look like a consistent user, not a rotating bot.
Domain affinity ensures the same IP is used for a session.
"""

# AP: AP-OMEGA-SIEVE-PROXY-v1.0.0

from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass, field
from typing import Optional

from .errors import ProxyError

logger = logging.getLogger("omega_sieve.proxy")


@dataclass
class ProxyConfig:
    """Configuration for a single proxy."""
    url: str
    type: str = "datacenter"  # "datacenter" | "residential"
    username: str = ""
    password: str = ""
    region: str = "auto"

    @property
    def auth(self) -> Optional[tuple[str, str]]:
        if self.username and self.password:
            return (self.username, self.password)
        return None


@dataclass
class ProxySession:
    """A sticky proxy session for a domain."""
    proxy: ProxyConfig
    domain: str
    created_at: float = 0.0
    last_used: float = 0.0
    failure_count: int = 0

    @property
    def healthy(self) -> bool:
        return self.failure_count < 3


class SovereignProxyPool:
    """Domain-affinity proxy pool for web scraping.

    Maintains sticky sessions per domain to avoid "impossible travel" detection.
    Falls back to round-robin if preferred proxy fails.
    """

    def __init__(self):
        self._sessions: dict[str, ProxySession] = {}
        self._proxies: list[ProxyConfig] = []
        self._round_robin_index: int = 0

    def configure(self, proxies: list[ProxyConfig]):
        """Set available proxies."""
        self._proxies = proxies
        logger.info(f"Proxy pool configured with {len(proxies)} proxies")

    def add_proxy(self, proxy: ProxyConfig):
        """Add a single proxy."""
        self._proxies.append(proxy)

    def get_proxy(self, url: str) -> Optional[ProxyConfig]:
        """Get a proxy for the given URL with domain affinity.

        Args:
            url: Target URL.

        Returns:
            ProxyConfig or None if no proxies configured.
        """
        if not self._proxies:
            return None

        domain = self._extract_domain(url)

        # Check for existing session
        if domain in self._sessions:
            session = self._sessions[domain]
            if session.healthy:
                session.last_used = time.monotonic()
                return session.proxy
            else:
                # Session is dead, remove it
                del self._sessions[domain]

        # Create new session with round-robin assignment
        proxy = self._next_proxy()
        if proxy:
            self._sessions[domain] = ProxySession(
                proxy=proxy, domain=domain,
                created_at=time.monotonic(), last_used=time.monotonic(),
            )

        return proxy

    def record_failure(self, url: str):
        """Record a failure for the proxy assigned to this URL."""
        domain = self._extract_domain(url)
        session = self._sessions.get(domain)
        if session:
            session.failure_count += 1
            logger.warning(f"Proxy failure for {domain} ({session.failure_count}/3)")

    def record_success(self, url: str):
        """Record a success for the proxy assigned to this URL."""
        domain = self._extract_domain(url)
        session = self._sessions.get(domain)
        if session:
            session.failure_count = 0

    def release_session(self, url: str):
        """Release a sticky session."""
        domain = self._extract_domain(url)
        self._sessions.pop(domain, None)

    def _next_proxy(self) -> Optional[ProxyConfig]:
        """Get next proxy in round-robin."""
        if not self._proxies:
            return None
        proxy = self._proxies[self._round_robin_index]
        self._round_robin_index = (self._round_robin_index + 1) % len(self._proxies)
        return proxy

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        match = re.search(r'https?://([^/]+)', url)
        if not match:
            raise ProxyError(f"Cannot extract domain from URL: {url}")
        return match.group(1)

    @property
    def active_sessions(self) -> int:
        return len(self._sessions)

    @property
    def healthy(self) -> bool:
        return len(self._proxies) > 0