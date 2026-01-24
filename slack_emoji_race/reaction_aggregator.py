"""リアクション集計モジュール。"""

import sys
from collections import defaultdict
from collections.abc import Iterator
from datetime import datetime, timedelta, timezone
from pathlib import Path

from slack_emoji_race.export_loader import load_all_messages

# 日本時間（JST, UTC+9）
JST = timezone(timedelta(hours=9))


def parse_timestamp_to_month(ts: str) -> str:
    """
    Slackのタイムスタンプ（ts）から日本時間の年月（YYYY-MM）を算出する。

    Args:
        ts: Slackのタイムスタンプ（例: "1730486400.000000"）

    Returns:
        年月文字列（例: "2025-01"）

    Raises:
        SystemExit: tsが不正な形式の場合
    """
    try:
        # tsは "整数部分.小数部分" の形式
        epoch_seconds = float(ts)
    except ValueError as e:
        msg = f"Error in parse_timestamp_to_month: Invalid timestamp format '{ts}': {e}"
        print(msg, file=sys.stderr)
        sys.exit(1)

    try:
        dt = datetime.fromtimestamp(epoch_seconds, tz=JST)
        return dt.strftime("%Y-%m")
    except (ValueError, OSError) as e:
        msg = f"Error in parse_timestamp_to_month: Failed to parse timestamp '{ts}': {e}"
        print(msg, file=sys.stderr)
        sys.exit(1)


def normalize_emoji_name(emoji_name: str) -> str:
    """
    絵文字名から肌色バリエーション（::skin-tone-X）を削除して正規化する。

    Args:
        emoji_name: 絵文字名（例: "thumbsup::skin-tone-2"）

    Returns:
        正規化された絵文字名（例: "thumbsup"）
    """
    # ::skin-tone- で分割して最初の部分を取得
    if "::skin-tone-" in emoji_name:
        return emoji_name.split("::skin-tone-")[0]
    return emoji_name


def extract_reactions_from_message(message: dict) -> list[dict]:
    """
    メッセージからリアクション配列を抽出する。

    Args:
        message: メッセージの辞書

    Returns:
        リアクションのリスト（reactionsフィールドがない場合は空リスト）
    """
    if "reactions" not in message:
        return []

    reactions = message["reactions"]
    if not isinstance(reactions, list):
        return []

    return reactions


def count_reactions_by_month(messages: Iterator[dict]) -> dict[str, dict[str, int]]:
    """
    メッセージのイテレータから月別リアクション集計辞書を構築する。

    Args:
        messages: メッセージのイテレータ

    Returns:
        月別集計辞書（{month: {emoji_name: count}}）

    Raises:
        SystemExit: メッセージのtsフィールドが不正な場合
    """
    aggregated: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for message in messages:
        if "ts" not in message:
            continue

        ts = message["ts"]
        month = parse_timestamp_to_month(ts)

        reactions = extract_reactions_from_message(message)

        for reaction in reactions:
            if "name" not in reaction or "count" not in reaction:
                continue

            emoji_name = normalize_emoji_name(reaction["name"])
            count = reaction["count"]

            if not isinstance(count, int):
                continue

            aggregated[month][emoji_name] += count

    # defaultdictを通常のdictに変換
    return {month: dict(counts) for month, counts in aggregated.items()}


def aggregate_reactions(export_dir: Path) -> dict[str, dict[str, int]]:
    """
    エクスポートディレクトリ全体のリアクションを集計する。

    Args:
        export_dir: Slackエクスポートのルートディレクトリ

    Returns:
        月別集計辞書（{month: {emoji_name: count}}）

    Raises:
        SystemExit: エクスポートディレクトリが読み取り不可、またはデータが不正な場合
    """
    messages = load_all_messages(export_dir)
    return count_reactions_by_month(messages)
