from __future__ import annotations

import logging
from typing import Tuple
from urllib.parse import urlparse

import httpx
from lxml import html
from readability import Document

from .config import MAX_EXTRACT_CHARS
from .models import ExtractedContent
from .utils import trim_text

logger = logging.getLogger(__name__)

USER_AGENT = "RaindropSummarizer/0.1 (+github.com/user)"


class ExtractionError(Exception):
    """Raised when content extraction fails."""


def detect_source(url: str) -> str:
    parsed = urlparse(url)
    host = parsed.hostname or ""
    if "youtube.com" in host or "youtu.be" in host:
        return "youtube"
    if host.endswith("x.com") or host.endswith("twitter.com"):
        return "x"
    return "web"


def fetch_html(url: str) -> str:
    logger.info("Fetching URL: %s", url)
    with httpx.Client(headers={"User-Agent": USER_AGENT}, timeout=20.0, follow_redirects=True) as client:
        try:
            response = client.get(url)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ExtractionError(f"HTTP fetch failed: {exc}") from exc
        return response.text


def extract_text(url: str) -> ExtractedContent:
    source = detect_source(url)
    html_text = fetch_html(url)
    if source == "youtube":
        text = _extract_youtube(html_text)
    elif source == "x":
        text = _extract_x(html_text)
    else:
        text = _extract_readability(html_text, url)
    cleaned = text.strip()
    if not cleaned:
        raise ExtractionError("Extracted text is empty.")
    trimmed = trim_text(cleaned, MAX_EXTRACT_CHARS)
    logger.info("Extracted %s characters from %s (source=%s)", len(trimmed), url, source)
    return ExtractedContent(text=trimmed, source=source, length=len(trimmed))


def _extract_youtube(html_text: str) -> str:
    tree = html.fromstring(html_text)
    title = tree.findtext(".//title") or ""
    description_nodes = tree.xpath("//meta[@name='description']/@content")
    description = description_nodes[0] if description_nodes else ""
    combined = "\n".join(filter(None, [title.strip(), description.strip()]))
    return combined


def _extract_x(html_text: str) -> str:
    tree = html.fromstring(html_text)
    og_description = tree.xpath("//meta[@property='og:description']/@content")
    description = og_description[0] if og_description else ""
    if not description:
        raise ExtractionError("Failed to extract X post content.")
    return description


def _extract_readability(html_text: str, url: str) -> str:
    doc = Document(html_text, url=url)
    summary_html = doc.summary(html_partial=True)
    tree = html.fromstring(summary_html)
    text = tree.text_content()
    return text
