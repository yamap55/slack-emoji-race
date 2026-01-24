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


def test_configure_chart_params_with_image_folder(tmp_path: Path) -> None:
    """configure_chart_paramsのテスト（画像フォルダ指定時）。"""
    # 画像フォルダを作成
    img_folder = tmp_path / "images"
    img_folder.mkdir()

    params = configure_chart_params(cumulative=False, img_label_folder=str(img_folder))

    # imageモードが設定されていることを確認
    assert params["tick_label_mode"] == "image"
    assert params["img_label_folder"] == str(img_folder.resolve())
    assert params["tick_image_mode"] == "trailing"


def test_configure_chart_params_with_nonexistent_image_folder(tmp_path: Path) -> None:
    """configure_chart_paramsのテスト（存在しない画像フォルダを指定）。"""
    nonexistent_folder = tmp_path / "nonexistent"

    params = configure_chart_params(cumulative=False, img_label_folder=str(nonexistent_folder))

    # 存在しないフォルダの場合、画像関連パラメータは設定されない
    assert "tick_label_mode" not in params
    assert "img_label_folder" not in params


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

    # 画像フォルダ指定なしの場合、列名はそのまま
    df_passed = call_args.kwargs["df"]
    assert "thumbsup" in df_passed.columns
    assert "saikou" in df_passed.columns


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


@patch("slack_emoji_race.chart_generator.bcr")
def test_generate_gif_with_image_folder(mock_bcr: MagicMock, tmp_path: Path) -> None:
    """画像フォルダ指定時のテスト（画像あり・なし混在）。"""
    # テスト用DataFrameを作成
    df = pd.DataFrame(
        {
            "thumbsup": [10, 15],
            "saikou": [5, 8],
        },
        index=["2025-01", "2025-02"],  # type: ignore
    )

    # 画像フォルダとファイルを作成
    img_folder = tmp_path / "images"
    img_folder.mkdir()
    (img_folder / "saikou.png").touch()  # saikouの画像だけ用意

    output_path = tmp_path / "test.gif"

    generate_gif(df, output_path, cumulative=False, img_label_folder=str(img_folder))

    # bar_chart_raceが呼ばれたことを確認
    mock_bcr.bar_chart_race.assert_called_once()
    call_args = mock_bcr.bar_chart_race.call_args

    # imageモードが設定されていることを確認
    assert call_args.kwargs["tick_label_mode"] == "image"
    assert call_args.kwargs["img_label_folder"] == str(img_folder.resolve())

    # DataFrameの列名は変換されずそのまま
    df_passed = call_args.kwargs["df"]
    assert "saikou" in df_passed.columns
    assert "thumbsup" in df_passed.columns
