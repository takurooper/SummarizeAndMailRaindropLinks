from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class RaindropItem:
    id: int
    link: str
    title: str
    created: datetime
    tags: List[str]
    note: Optional[str] = None


@dataclass
class ExtractedContent:
    text: str
    source: str  # e.g., "youtube", "x", "web"
    length: int


@dataclass
class SummaryResult:
    item: RaindropItem
    status: str  # "success" | "failed"
    summary: Optional[str] = None
    error: Optional[str] = None

    def is_success(self) -> bool:
        return self.status == "success"


@dataclass
class EmailContext:
    batch_date_str: str
    results: List[SummaryResult] = field(default_factory=list)
