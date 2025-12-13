"""Bar Chart Race生成モジュール。"""

import sys
from pathlib import Path

import bar_chart_race as bcr
import pandas as pd


def configure_chart_params() -> dict:
    """
    bar_chart_raceのパラメータ設定を返す。

    Returns:
        パラメータの辞書
    """
    return {
        "n_bars": 20,
        "orientation": "h",
        "title": "Slack Emoji Reactions per Month",
        "bar_size": 0.95,
        "period_length": 500,
        "steps_per_period": 10,
        "interpolate_period": True,
        "bar_label_size": 7,
        "tick_label_size": 7,
        "period_label": {"x": 0.99, "y": 0.99, "ha": "right", "va": "top"},
    }


def generate_gif(df: pd.DataFrame, output_path: Path) -> None:
    """
    Bar Chart RaceのGIFを生成する。

    Args:
        df: 集計済みのpandas DataFrame（index: 月、columns: 絵文字名）
        output_path: 出力GIFファイルのパス

    Raises:
        SystemExit: GIF生成に失敗した場合
    """
    if df.empty:
        print("Error in generate_gif: DataFrame is empty", file=sys.stderr)
        sys.exit(1)

    params = configure_chart_params()

    try:
        bcr.bar_chart_race(
            df=df,
            filename=str(output_path),
            **params,
        )
    except Exception as e:
        print(f"Error in generate_gif: Failed to generate GIF: {e}", file=sys.stderr)
        print("Note: Make sure ffmpeg is installed if you see encoding errors.", file=sys.stderr)
        sys.exit(1)

