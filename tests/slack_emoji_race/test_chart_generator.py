"""ChartGeneratorモジュールのテスト。"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from slack_emoji_race.chart_generator import configure_chart_params, generate_gif


def test_configure_chart_params() -> None:
    """configure_chart_paramsのテスト。"""
    params = configure_chart_params()

    assert params["n_bars"] == 20
    assert params["orientation"] == "h"
    assert params["title"] == "Slack Emoji Reactions per Month"
    assert "bar_size" in params
    assert "period_length" in params


@patch("slack_emoji_race.chart_generator.bcr")
def test_generate_gif(mock_bcr: MagicMock, tmp_path: Path) -> None:
    """generate_gifのテスト（モック使用）。"""
    # テスト用DataFrameを作成
    df = pd.DataFrame(
        {
            "saikou": [5, 10],
            "thumbsup": [3, 7],
        },
        index=["2025-01", "2025-02"],  # type: ignore
    )

    output_path = tmp_path / "test.gif"

    generate_gif(df, output_path)

    # bar_chart_raceが呼ばれたことを確認
    mock_bcr.bar_chart_race.assert_called_once()
    call_args = mock_bcr.bar_chart_race.call_args

    # 引数の確認
    assert call_args.kwargs["n_bars"] == 20
    assert call_args.kwargs["orientation"] == "h"
    assert call_args.kwargs["title"] == "Slack Emoji Reactions per Month"


def test_generate_gif_empty_dataframe(tmp_path: Path) -> None:
    """空のDataFrameの場合のテスト。"""
    df = pd.DataFrame()

    output_path = tmp_path / "test.gif"

    with pytest.raises(SystemExit):
        generate_gif(df, output_path)

