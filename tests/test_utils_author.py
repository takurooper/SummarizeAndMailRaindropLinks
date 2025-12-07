from __future__ import annotations

from summarizeandmailraindroplinks.utils import split_author_and_summary


def test_split_author_and_summary_extracts_author():
    summary = "著者/投稿者: 山田太郎\n一行要約\nポイント1"
    author, remaining = split_author_and_summary(summary)
    assert author == "山田太郎"
    assert "一行要約" in remaining


def test_split_author_and_summary_defaults_when_missing():
    summary = "一行要約\nポイント1"
    author, remaining = split_author_and_summary(summary)
    assert "名無しの投稿者" in author
    assert remaining == summary
