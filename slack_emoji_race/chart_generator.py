"""Bar Chart Race生成モジュール。"""

import sys
from pathlib import Path

import bar_chart_race as bcr
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import pandas as pd


def get_japanese_font_path() -> Path:
    """
    日本語対応フォントファイルのパスを取得する。

    Returns:
        フォントファイルのPathオブジェクト

    Raises:
        SystemExit: フォントが見つからない場合
    """
    # Noto Sans CJKフォントファイルのパス
    font_paths = [
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
        Path("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"),
    ]

    for font_path in font_paths:
        if font_path.exists():
            return font_path

    msg = "Error: Japanese font (Noto Sans CJK) not found. Please install fonts-noto-cjk package."
    print(msg, file=sys.stderr)
    sys.exit(1)


def configure_chart_params() -> dict:
    """
    bar_chart_raceのパラメータ設定を返す。

    Returns:
        パラメータの辞書
    """
    font_path = get_japanese_font_path()
    font_prop = fm.FontProperties(fname=str(font_path))
    font_family = font_prop.get_name()

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
        "shared_fontdict": {"family": font_family},
    }


def configure_fonts() -> None:
    """
    matplotlibのフォント設定を構成する。
    文字化けを防ぐため、日本語フォントを登録して設定する。
    """
    font_path = get_japanese_font_path()
    fm.fontManager.addfont(str(font_path))
    font_prop = fm.FontProperties(fname=str(font_path))
    font_name = font_prop.get_name()

    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = [
        font_name,
        "DejaVu Sans",
        "Bitstream Vera Sans",
        "Computer Modern Sans Serif",
        "Lucida Grande",
        "Verdana",
        "Geneva",
        "Lucid",
        "Arial",
        "Helvetica",
        "Avant Garde",
        "sans-serif",
    ]
    plt.rcParams["axes.unicode_minus"] = False


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

    # フォント設定を適用
    configure_fonts()

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

