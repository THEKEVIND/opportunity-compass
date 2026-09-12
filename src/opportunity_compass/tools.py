"""Strands tools for inspecting URLs and producing auditable assessments."""

from __future__ import annotations

import json
import socket
from datetime import datetime
from html.parser import HTMLParser
from ipaddress import ip_address
from urllib.parse import urlparse

import httpx
from strands import tool

from .models import Opportunity
from .scoring import assess_opportunity

ALLOWED_SCHEMES = {"https"}
MAX_RESPONSE_BYTES = 1_000_000
MAX_REDIRECTS = 5


class _VisibleTextParser(HTMLParser):
    """Extract human-visible text without executing or preserving page markup."""

    def __init__(self) -> None:
        super().__init__()
        self._ignored_depth = 0
        self.parts: list[str] = []
        self.title_parts: list[str] = []
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del attrs
        if tag in {"script", "style", "noscript"}:
            self._ignored_depth += 1
        elif tag == "title":
            self._in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"} and self._ignored_depth:
            self._ignored_depth -= 1
        elif tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._ignored_depth:
            return
        if self._in_title:
            self.title_parts.append(data)
        self.parts.append(data)


def _validate_public_https_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in ALLOWED_SCHEMES or not parsed.hostname:
        raise ValueError("Only public HTTPS URLs are accepted")
    host = parsed.hostname.lower()
    if host in {"localhost", "127.0.0.1", "::1"} or host.endswith(".local"):
        raise ValueError("Local network URLs are not accepted")
    try:
        addresses = {item[4][0] for item in socket.getaddrinfo(host, parsed.port or 443)}
    except socket.gaierror as exc:
        raise ValueError("The URL hostname could not be resolved") from exc
    if not addresses:
        raise ValueError("The URL hostname did not resolve to an address")
    for address in addresses:
        parsed_address = ip_address(address)
        if not parsed_address.is_global:
            raise ValueError("Private, loopback, and reserved network addresses are not accepted")


def _fetch_with_checked_redirects(url: str) -> httpx.Response:
    """Fetch a bounded public page while validating every redirect target."""
    current_url = url
    with httpx.Client(follow_redirects=False, timeout=15) as client:
        for _ in range(MAX_REDIRECTS + 1):
            _validate_public_https_url(current_url)
            with client.stream(
                "GET",
                current_url,
                # Request an uncompressed body. Some CDNs advertise an encoding
                # that intermediary proxies do not preserve correctly, which can
                # make an otherwise public page fail during decompression.
                headers={
                    "User-Agent": "OpportunityCompass/0.1",
                    "Accept-Encoding": "identity",
                },
            ) as response:
                if response.is_redirect:
                    location = response.headers.get("location")
                    if not location:
                        raise ValueError("Redirect response did not include a destination")
                    current_url = str(response.url.join(location))
                    continue
                content = b""
                for chunk in response.iter_bytes():
                    remaining = MAX_RESPONSE_BYTES - len(content)
                    if remaining <= 0:
                        break
                    content += chunk[:remaining]
                return httpx.Response(
                    status_code=response.status_code,
                    headers=response.headers,
                    content=content,
                    request=response.request,
                    extensions=response.extensions,
                )
    raise ValueError(f"The page exceeded the {MAX_REDIRECTS}-redirect limit")


@tool
def inspect_public_page(url: str) -> str:
    """Fetch a public HTTPS page and return status, final URL, title, and visible text excerpt."""
    response = _fetch_with_checked_redirects(url)
    text = response.text
    parser = _VisibleTextParser()
    parser.feed(text)
    visible_text = " ".join(" ".join(parser.parts).split())
    title = " ".join(" ".join(parser.title_parts).split())
    return json.dumps(
        {
            "status_code": response.status_code,
            "final_url": str(response.url),
            "title": title[:300],
            "excerpt": visible_text[:8_000],
        },
        ensure_ascii=False,
    )


@tool
def score_verified_opportunity(opportunity_json: str, current_time_iso: str | None = None) -> str:
    """Score verified opportunity facts; return a transparent verdict and next action."""
    opportunity = Opportunity.model_validate_json(opportunity_json)
    current_time = datetime.fromisoformat(current_time_iso) if current_time_iso else None
    assessment = assess_opportunity(opportunity, now=current_time)
    return assessment.model_dump_json(indent=2)
