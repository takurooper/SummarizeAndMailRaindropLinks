from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Iterable, List

from .config import JST, TAG_CONFIRMED, TAG_DELIVERED, TAG_FAILED
from .models import RaindropItem

logger = logging.getLogger(__name__)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def to_jst(dt: datetime) -> datetime:
    return dt.astimezone(JST)


def parse_raindrop_datetime(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00") if value.endswith("Z") else value
    try:
        return datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(f"Invalid datetime format: {value}") from exc


def is_recent(item: RaindropItem, threshold_jst: datetime) -> bool:
    created_jst = item.created.astimezone(JST)
    return created_jst >= threshold_jst


def has_excluded_tag(tags: Iterable[str]) -> bool:
    excluded = {TAG_CONFIRMED, TAG_DELIVERED, TAG_FAILED}
    return any(tag in excluded for tag in tags)


def filter_new_items(items: List[RaindropItem], threshold_jst: datetime) -> List[RaindropItem]:
    filtered: List[RaindropItem] = []
    for item in items:
        if not is_recent(item, threshold_jst):
            continue
        if has_excluded_tag(item.tags):
            continue
        filtered.append(item)
    return filtered


def append_note(original: str | None, addition: str) -> str:
    if not original:
        return addition
    separator = "\n\n" if not original.endswith("\n\n") else ""
    return f"{original}{separator}{addition}"


def trim_text(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars]


def split_author_and_summary(summary: str) -> tuple[str, str]:
    lines = [line.strip() for line in summary.splitlines() if line.strip()]
    if not lines:
        return "名無しの投稿者（情報不足）", summary

    first = lines[0]
    prefixes = ("著者/投稿者:", "著者:", "投稿者:")
    if any(first.startswith(p) for p in prefixes):
        author_value = first.split(":", 1)[1].strip() or "名無しの投稿者（情報不足）"
        remaining = "\n".join(lines[1:]).strip()
        return author_value, remaining or summary

    return "名無しの投稿者（情報不足）", summary


def threshold_from_now(now_jst: datetime, days: int) -> datetime:
    return now_jst - timedelta(days=days)
