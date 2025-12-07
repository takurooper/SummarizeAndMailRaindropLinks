from __future__ import annotations

import logging
from datetime import datetime
from typing import List, Optional

import httpx

from .config import TAG_CONFIRMED, TAG_DELIVERED, TAG_FAILED, UNSORTED_COLLECTION_ID
from .models import RaindropItem
from .utils import append_note, parse_raindrop_datetime

logger = logging.getLogger(__name__)


class RaindropClient:
    def __init__(self, token: str, base_url: str = "https://api.raindrop.io"):
        self._client = httpx.Client(
            base_url=base_url, headers={"Authorization": f"Bearer {token}"}, timeout=20.0
        )

    def close(self) -> None:
        self._client.close()

    def fetch_unsorted_items(self, perpage: int = 50, max_pages: int = 20) -> List[RaindropItem]:
        items: List[RaindropItem] = []
        for page in range(max_pages):
            response = self._client.get(
                f"/rest/v1/raindrops/{UNSORTED_COLLECTION_ID}",
                params={"page": page, "perpage": perpage, "sort": "-created"},
            )
            response.raise_for_status()
            data = response.json()
            page_items = data.get("items", [])
            logger.info("Fetched %s items from page %s", len(page_items), page)
            for raw in page_items:
                item = self._to_model(raw)
                items.append(item)
            if len(page_items) < perpage:
                break
        return items

    def append_note_and_tags(
        self,
        item: RaindropItem,
        note_addition: Optional[str],
        extra_tags: List[str],
    ) -> None:
        merged_note = append_note(item.note, note_addition) if note_addition else item.note or ""
        merged_tags = list({*item.tags, *extra_tags})
        payload = {"note": merged_note, "tags": merged_tags}
        logger.info("Updating Raindrop item %s with tags=%s", item.id, merged_tags)
        response = self._client.put(f"/rest/v1/raindrop/{item.id}", json=payload)
        response.raise_for_status()

    @staticmethod
    def _to_model(raw: dict) -> RaindropItem:
        return RaindropItem(
            id=raw["_id"] if "_id" in raw else raw["id"],
            link=raw["link"],
            title=raw.get("title") or raw.get("domain") or raw["link"],
            created=parse_raindrop_datetime(raw["created"]),
            tags=raw.get("tags", []),
            note=raw.get("note") or None,
        )


EXCLUDED_TAGS = {TAG_CONFIRMED, TAG_DELIVERED, TAG_FAILED}
