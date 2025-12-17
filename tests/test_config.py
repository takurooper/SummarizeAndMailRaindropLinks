from __future__ import annotations

import importlib
import os
from types import ModuleType

import pytest

import raindrop_digest.config as config


def _reload_config() -> ModuleType:
    return importlib.reload(config)


def test_batch_lookback_days_default(monkeypatch: pytest.MonkeyPatch) -> None:
    original = os.getenv("BATCH_LOOKBACK_DAYS")
    try:
        monkeypatch.delenv("BATCH_LOOKBACK_DAYS", raising=False)
        reloaded = _reload_config()
        assert reloaded.BATCH_LOOKBACK_DAYS == 1
    finally:
        if original is None:
            monkeypatch.delenv("BATCH_LOOKBACK_DAYS", raising=False)
        else:
            monkeypatch.setenv("BATCH_LOOKBACK_DAYS", original)
        _reload_config()


def test_batch_lookback_days_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    original = os.getenv("BATCH_LOOKBACK_DAYS")
    try:
        monkeypatch.setenv("BATCH_LOOKBACK_DAYS", "3")
        reloaded = _reload_config()
        assert reloaded.BATCH_LOOKBACK_DAYS == 3
    finally:
        if original is None:
            monkeypatch.delenv("BATCH_LOOKBACK_DAYS", raising=False)
        else:
            monkeypatch.setenv("BATCH_LOOKBACK_DAYS", original)
        _reload_config()


@pytest.mark.parametrize("value", ["abc", "1.5", "3 days"])
def test_batch_lookback_days_invalid_integer_raises(monkeypatch: pytest.MonkeyPatch, value: str) -> None:
    original = os.getenv("BATCH_LOOKBACK_DAYS")
    try:
        monkeypatch.setenv("BATCH_LOOKBACK_DAYS", value)
        with pytest.raises(ValueError, match=r"Environment variable BATCH_LOOKBACK_DAYS must be an integer"):
            _reload_config()
    finally:
        if original is None:
            monkeypatch.delenv("BATCH_LOOKBACK_DAYS", raising=False)
        else:
            monkeypatch.setenv("BATCH_LOOKBACK_DAYS", original)
        _reload_config()


@pytest.mark.parametrize("value", ["0", "-1"])
def test_batch_lookback_days_too_small_raises(monkeypatch: pytest.MonkeyPatch, value: str) -> None:
    original = os.getenv("BATCH_LOOKBACK_DAYS")
    try:
        monkeypatch.setenv("BATCH_LOOKBACK_DAYS", value)
        with pytest.raises(ValueError, match=r"Environment variable BATCH_LOOKBACK_DAYS must be >= 1"):
            _reload_config()
    finally:
        if original is None:
            monkeypatch.delenv("BATCH_LOOKBACK_DAYS", raising=False)
        else:
            monkeypatch.setenv("BATCH_LOOKBACK_DAYS", original)
        _reload_config()
