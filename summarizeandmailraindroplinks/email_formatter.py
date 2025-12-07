from __future__ import annotations

from datetime import datetime
from typing import List

from .config import JST, SUMMARY_CHAR_LIMIT, TAG_FAILED
from .models import EmailContext, SummaryResult


def format_datetime_jst(dt: datetime) -> str:
    return dt.astimezone(JST).strftime("%Y-%m-%d %H:%M")


def build_email_subject(batch_date: datetime) -> str:
    date_str = batch_date.astimezone(JST).strftime("%Y-%m-%d")
    return f"【要約まとめ】{date_str} 直近3日版"


def build_email_body(batch_date: datetime, results: List[SummaryResult]) -> str:
    header = "こんにちは。過去3日分のブックマークしたリンクの要約です。\n"
    if not results:
        return header + "\n今回は新着対象がありませんでした。"

    lines = [header]
    for idx, result in enumerate(results, start=1):
        item = result.item
        lines.append("====================")
        lines.append(f"{idx}. タイトル: {item.title}")
        lines.append(f"URL: {item.link}")
        lines.append(f"追加日時: {format_datetime_jst(item.created)}")
        lines.append("\n▼サマリー")
        if result.is_success() and result.summary:
            lines.append(result.summary.strip())
        else:
            lines.append("このURLは要約に失敗したので、手動確認してね。")
            if result.error:
                lines.append(f"(error: {result.error})")
        lines.append("")  # spacer

    lines.append(f"\n※ 各要約は最大{SUMMARY_CHAR_LIMIT}文字目安で生成しています。")
    return "\n".join(lines)
