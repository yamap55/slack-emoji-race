"""ChartGeneratorモジュールのテスト。"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from slack_emoji_race.chart_generator import (
    configure_chart_params,
    generate_gif,
    get_chart_title,
)


def test_get_chart_title() -> None:
    """get_chart_titleのテスト。"""
    assert get_chart_title(False) == "Slack Emoji Reactions per Month"
    assert get_chart_title(True) == "Slack Emoji Reactions (Cumulative)"


def test_configure_chart_params() -> None:
    """configure_chart_paramsのテスト（月別モード）。"""
    params = configure_chart_params(cumulative=False)

    assert params["n_bars"] == 20
    assert params["orientation"] == "h"
    assert params["title"] == "Slack Emoji Reactions per Month"
    assert "bar_size" in params
    assert "period_length" in params


def test_configure_chart_params_cumulative() -> None:
    """configure_chart_paramsのテスト（累計モード）。"""
    params = configure_chart_params(cumulative=True)

    assert params["title"] == "Slack Emoji Reactions (Cumulative)"


@patch("slack_emoji_race.chart_generator.bcr")
def test_generate_gif(mock_bcr: MagicMock, tmp_path: Path) -> None:
    """generate_gifのテスト（モック使用、月別モード）。"""
    # テスト用DataFrameを作成
    df = pd.DataFrame(
        {
            "saikou": [5, 10],
            "thumbsup": [3, 7],
        },
        index=["2025-01", "2025-02"],  # type: ignore
    )

    output_path = tmp_path / "test.gif"

    generate_gif(df, output_path, cumulative=False)

    # bar_chart_raceが呼ばれたことを確認
    mock_bcr.bar_chart_race.assert_called_once()
    call_args = mock_bcr.bar_chart_race.call_args

    # 引数の確認
    assert call_args.kwargs["n_bars"] == 20
    assert call_args.kwargs["orientation"] == "h"
    assert call_args.kwargs["title"] == "Slack Emoji Reactions per Month"


@patch("slack_emoji_race.chart_generator.bcr")
def test_generate_gif_cumulative(mock_bcr: MagicMock, tmp_path: Path) -> None:
    """generate_gifのテスト（モック使用、累計モード）。"""
    # テスト用DataFrameを作成
    df = pd.DataFrame(
        {
            "saikou": [5, 15],
            "thumbsup": [3, 3],
        },
        index=["2025-01", "2025-02"],  # type: ignore
    )

    output_path = tmp_path / "test.gif"

    generate_gif(df, output_path, cumulative=True)

    # bar_chart_raceが呼ばれたことを確認
    mock_bcr.bar_chart_race.assert_called_once()
    call_args = mock_bcr.bar_chart_race.call_args

    # タイトルが累計モードであることを確認
    assert call_args.kwargs["title"] == "Slack Emoji Reactions (Cumulative)"


def test_generate_gif_empty_dataframe(tmp_path: Path) -> None:
    """空のDataFrameの場合のテスト。"""
    df = pd.DataFrame()

    output_path = tmp_path / "test.gif"

    with pytest.raises(SystemExit):
        generate_gif(df, output_path)

