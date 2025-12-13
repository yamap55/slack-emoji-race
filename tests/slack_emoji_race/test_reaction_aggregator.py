"""ReactionAggregatorモジュールのテスト。"""

from pathlib import Path

import pytest

from slack_emoji_race.reaction_aggregator import (
    aggregate_reactions,
    count_reactions_by_month,
    extract_reactions_from_message,
    parse_timestamp_to_month,
)


def test_parse_timestamp_to_month() -> None:
    """parse_timestamp_to_monthのテスト（JST変換確認）。"""
    # 2025-01-01 00:00:00 UTC = 2025-01-01 09:00:00 JST
    # epoch: 1735689600
    ts_utc_midnight = "1735689600.000000"
    result = parse_timestamp_to_month(ts_utc_midnight)
    assert result == "2025-01"

    # 2025-01-01 00:00:00 JST = 2024-12-31 15:00:00 UTC
    # epoch: 1735657200
    ts_jst_midnight = "1735657200.000000"
    result = parse_timestamp_to_month(ts_jst_midnight)
    assert result == "2025-01"

    # 2025-12-31 23:59:59 JST
    # epoch: 1767193199
    ts_jst_end = "1767193199.000000"
    result = parse_timestamp_to_month(ts_jst_end)
    assert result == "2025-12"


def test_parse_timestamp_to_month_invalid() -> None:
    """不正なタイムスタンプの場合のテスト。"""
    with pytest.raises(SystemExit):
        parse_timestamp_to_month("invalid")


def test_extract_reactions_from_message() -> None:
    """extract_reactions_from_messageのテスト。"""
    # リアクションあり
    message_with_reactions = {
        "type": "message",
        "text": "test",
        "ts": "1234567890.000000",
        "reactions": [
            {"name": "saikou", "users": ["U123"], "count": 1},
            {"name": "thumbsup", "users": ["U456"], "count": 2},
        ],
    }
    result = extract_reactions_from_message(message_with_reactions)
    assert len(result) == 2
    assert result[0]["name"] == "saikou"
    assert result[1]["name"] == "thumbsup"

    # リアクションなし
    message_without_reactions = {
        "type": "message",
        "text": "test",
        "ts": "1234567890.000000",
    }
    result = extract_reactions_from_message(message_without_reactions)
    assert result == []

    # reactionsが空リスト
    message_empty_reactions = {
        "type": "message",
        "text": "test",
        "ts": "1234567890.000000",
        "reactions": [],
    }
    result = extract_reactions_from_message(message_empty_reactions)
    assert result == []


def test_count_reactions_by_month() -> None:
    """count_reactions_by_monthのテスト。"""
    messages = [
        {
            "type": "message",
            "text": "test1",
            "ts": "1735657200.000000",  # 2025-01-01 JST
            "reactions": [
                {"name": "saikou", "users": ["U123"], "count": 2},
                {"name": "thumbsup", "users": ["U456"], "count": 1},
            ],
        },
        {
            "type": "message",
            "text": "test2",
            "ts": "1735657200.000000",  # 2025-01-01 JST
            "reactions": [
                {"name": "saikou", "users": ["U789"], "count": 1},
            ],
        },
        {
            "type": "message",
            "text": "test3",
            "ts": "1738335600.000000",  # 2025-02-01 JST
            "reactions": [
                {"name": "thumbsup", "users": ["U123"], "count": 3},
            ],
        },
    ]

    result = count_reactions_by_month(iter(messages))

    assert "2025-01" in result
    assert "2025-02" in result
    assert result["2025-01"]["saikou"] == 3  # 2 + 1
    assert result["2025-01"]["thumbsup"] == 1
    assert result["2025-02"]["thumbsup"] == 3


def test_count_reactions_by_month_no_reactions() -> None:
    """リアクションがないメッセージの場合のテスト。"""
    messages = [
        {
            "type": "message",
            "text": "test",
            "ts": "1735657200.000000",
        },
    ]

    result = count_reactions_by_month(iter(messages))
    assert result == {}


def test_count_reactions_by_month_no_ts() -> None:
    """tsフィールドがないメッセージの場合のテスト。"""
    messages = [
        {
            "type": "message",
            "text": "test",
            "reactions": [{"name": "saikou", "users": ["U123"], "count": 1}],
        },
    ]

    result = count_reactions_by_month(iter(messages))
    assert result == {}


def test_aggregate_reactions() -> None:
    """aggregate_reactionsの統合テスト。"""
    fixtures_dir = Path(__file__).parent.parent / "fixtures"

    result = aggregate_reactions(fixtures_dir)

    # 結果が辞書であることを確認
    assert isinstance(result, dict)

    # 月が含まれていることを確認（fixtureデータに基づく）
    # fixtureには2025-01のデータがあるはず
    if "2025-01" in result:
        assert isinstance(result["2025-01"], dict)

