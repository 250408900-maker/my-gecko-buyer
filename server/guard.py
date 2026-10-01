from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse


def is_public_url(url: str) -> bool:
    """Return True only for HTTPS URLs resolving entirely to public IPs."""

    try:
        parsed = urlparse(url)

        # Only HTTPS URLs are allowed.
        if parsed.scheme.lower() != "https":
            return False

        hostname = parsed.hostname
        if not hostname:
            return False

        # Resolve the hostname. If it cannot be resolved, reject it.
        try:
            infos = socket.getaddrinfo(
                hostname,
                parsed.port or 443,
                type=socket.SOCK_STREAM,
            )
        except (socket.gaierror, OSError):
            return False

        if not infos:
            return False

        for info in infos:
            address = info[4][0]

            try:
                ip = ipaddress.ip_address(address)
            except ValueError:
                return False

            if (
                ip.is_private
                or ip.is_loopback
                or ip.is_link_local
                or ip.is_reserved
                or ip.is_multicast
                or ip.is_unspecified
            ):
                return False

        return True

    except (ValueError, TypeError):
        return False