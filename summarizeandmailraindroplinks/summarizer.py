from __future__ import annotations

import logging
from typing import List, Optional, Sequence

from openai import APIConnectionError, APITimeoutError, OpenAI, RateLimitError

from .config import IMAGE_TEXT_THRESHOLD, MIN_IMAGES_FOR_SUMMARY
from .prompts import summarization_system_prompt

logger = logging.getLogger(__name__)


class SummaryError(Exception):
    """Raised when summarization fails."""


class SummaryConnectionError(SummaryError):
    """Raised when summarization fails due to upstream connection issues."""


class SummaryRateLimitError(SummaryError):
    """Raised when summarization fails due to rate limits."""


class Summarizer:
    def __init__(self, api_key: str, model: str = "gpt-4.1-mini", client: Optional[OpenAI] = None):
        if not model or not model.strip():
            raise ValueError("OpenAI model must be provided.")
        self._client = client or OpenAI(api_key=api_key)
        self._model = model.strip()

    def summarize(self, text: str, images: Optional[List[str]] = None) -> str:
        include_images = self._should_include_images(text, images or [])
        logger.info(
            "Summarization request: chars=%s images=%s include_images=%s",
            len(text),
            len(images or []),
            include_images,
        )
        user_content = self._build_user_content(text, images or [], include_images)
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {
                        "role": "system",
                        "content": summarization_system_prompt(),
                    },
                    {"role": "user", "content": user_content},
                ],
                temperature=0.3,
            )
        except RateLimitError as exc:
            raise SummaryRateLimitError(f"OpenAI rate limit: {exc}") from exc
        except (APIConnectionError, APITimeoutError) as exc:
            raise SummaryConnectionError(f"OpenAI connection failed: {exc}") from exc
        except Exception as exc:  # noqa: BLE001
            raise SummaryError(f"OpenAI API call failed: {exc}") from exc

        if not response.choices:
            raise SummaryError("OpenAI response has no choices.")
        content: Optional[str] = response.choices[0].message.content
        if not content:
            raise SummaryError("OpenAI returned empty content.")
        logger.info("Summary generated (%s chars)", len(content))
        return content.strip()

    @staticmethod
    def _should_include_images(text: str, images: Sequence[str]) -> bool:
        return len(text) <= IMAGE_TEXT_THRESHOLD and len(images) >= MIN_IMAGES_FOR_SUMMARY

    @staticmethod
    def _build_user_content(text: str, images: Sequence[str], include_images: bool) -> list:
        if not include_images or not images:
            return [{"type": "text", "text": text}]
        content = [{"type": "text", "text": text}]
        for img in images:
            content.append({"type": "image_url", "image_url": {"url": img}})
        return content
