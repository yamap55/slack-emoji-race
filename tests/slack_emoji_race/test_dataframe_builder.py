"""DataFrameBuilderモジュールのテスト。"""

import pandas as pd

from slack_emoji_race.dataframe_builder import (
    build_cumulative_dataframe,
    build_dataframe,
    get_all_emojis,
    get_all_months,
)


def test_get_all_months() -> None:
    """get_all_monthsのテスト。"""
    aggregated_data = {
        "2025-02": {"saikou": 10},
        "2025-01": {"saikou": 5},
        "2025-03": {"saikou": 15},
    }

    result = get_all_months(aggregated_data)
    assert result == ["2025-01", "2025-02", "2025-03"]


def test_get_all_emojis() -> None:
    """get_all_emojisのテスト。"""
    aggregated_data = {
        "2025-01": {"saikou": 5, "thumbsup": 3},
        "2025-02": {"saikou": 10, "heart": 2},
    }

    result = get_all_emojis(aggregated_data)
    assert result == {"saikou", "thumbsup", "heart"}


def test_build_dataframe() -> None:
    """build_dataframeのテスト。"""
    aggregated_data = {
        "2025-01": {"saikou": 5, "thumbsup": 3},
        "2025-02": {"saikou": 10, "heart": 2},
    }

    df = build_dataframe(aggregated_data)

    # 形状の確認
    assert df.shape == (2, 3)  # 2ヶ月、3種類の絵文字

    # インデックスがDatetimeIndexであることを確認
    assert isinstance(df.index, pd.DatetimeIndex)
    assert len(df.index) == 2
    assert df.index[0] == pd.Timestamp("2025-01-01")
    assert df.index[1] == pd.Timestamp("2025-02-01")

    # カラムが絵文字名であることを確認（ソート順）
    assert list(df.columns) == ["heart", "saikou", "thumbsup"]

    # 値の確認（DatetimeIndexでは完全な日付形式でアクセス）
    assert df.loc["2025-01-01", "saikou"] == 5
    assert df.loc["2025-01-01", "thumbsup"] == 3
    assert df.loc["2025-01-01", "heart"] == 0  # 存在しない場合は0

    assert df.loc["2025-02-01", "saikou"] == 10
    assert df.loc["2025-02-01", "heart"] == 2
    assert df.loc["2025-02-01", "thumbsup"] == 0  # 存在しない場合は0


def test_build_dataframe_empty() -> None:
    """空の集計データの場合のテスト。"""
    aggregated_data: dict[str, dict[str, int]] = {}

    df = build_dataframe(aggregated_data)

    assert df.shape == (0, 0)
    assert isinstance(df, pd.DataFrame)


def test_build_dataframe_single_month() -> None:
    """単一月の場合のテスト。"""
    aggregated_data = {
        "2025-01": {"saikou": 5},
    }

    df = build_dataframe(aggregated_data)

    assert df.shape == (1, 1)
    assert df.loc["2025-01-01", "saikou"] == 5


def test_build_cumulative_dataframe() -> None:
    """build_cumulative_dataframeのテスト（累計モード）。"""
    aggregated_data = {
        "2025-01": {"saikou": 5, "thumbsup": 3},
        "2025-02": {"saikou": 10, "heart": 2},
    }

    df = build_cumulative_dataframe(aggregated_data)

    # 形状の確認
    assert df.shape == (2, 3)  # 2ヶ月、3種類の絵文字

    # インデックスがDatetimeIndexであることを確認
    assert isinstance(df.index, pd.DatetimeIndex)
    assert len(df.index) == 2

    # カラムが絵文字名であることを確認（ソート順）
    assert list(df.columns) == ["heart", "saikou", "thumbsup"]

    # 累計値の確認
    # 2025-01: 初月なのでそのまま
    assert df.loc["2025-01-01", "saikou"] == 5
    assert df.loc["2025-01-01", "thumbsup"] == 3
    assert df.loc["2025-01-01", "heart"] == 0

    # 2025-02: 累計値（前月 + 当月）
    assert df.loc["2025-02-01", "saikou"] == 15  # 5 + 10
    assert df.loc["2025-02-01", "thumbsup"] == 3  # 3 + 0（変化なし）
    assert df.loc["2025-02-01", "heart"] == 2  # 0 + 2


def test_build_cumulative_dataframe_empty() -> None:
    """空の集計データの場合のテスト（累計モード）。"""
    aggregated_data: dict[str, dict[str, int]] = {}

    df = build_cumulative_dataframe(aggregated_data)

    assert df.shape == (0, 0)
    assert isinstance(df, pd.DataFrame)


def test_build_cumulative_dataframe_single_month() -> None:
    """単一月の場合のテスト（累計モード）。"""
    aggregated_data = {
        "2025-01": {"saikou": 5},
    }

    df = build_cumulative_dataframe(aggregated_data)

    assert df.shape == (1, 1)
    assert df.loc["2025-01-01", "saikou"] == 5
