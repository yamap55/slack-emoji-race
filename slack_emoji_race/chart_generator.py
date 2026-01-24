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


def get_chart_title(cumulative: bool) -> str:
    """
    チャートタイトルを取得する。

    Args:
        cumulative: 累計モードの場合True

    Returns:
        チャートタイトル文字列
    """
    if cumulative:
        return "Slack Emoji Reactions (Cumulative)"
    return "Slack Emoji Reactions per Month"


def configure_chart_params(
    cumulative: bool = False, img_label_folder: str | Path | None = None
) -> dict:
    """
    bar_chart_raceのパラメータ設定を返す。

    Args:
        cumulative: 累計モードの場合True
        img_label_folder: 画像ラベルフォルダのパス（Noneの場合は画像を使用しない）

    Returns:
        パラメータの辞書
    """
    font_path = get_japanese_font_path()
    font_prop = fm.FontProperties(fname=str(font_path))
    font_family = font_prop.get_name()

    params = {
        "n_bars": 20,
        "orientation": "h",
        "title": get_chart_title(cumulative),
        "bar_size": 0.95,
        "period_length": 500,
        "steps_per_period": 10,
        "interpolate_period": True,
        "bar_label_font": 7,  # フォーク版では bar_label_font を使用
        "tick_label_font": 7,  # フォーク版では tick_label_font を使用
        "period_label": {"x": 0.99, "y": 0.15, "ha": "right", "va": "bottom"},
        "shared_fontdict": {"family": font_family},
    }

    # 画像フォルダが指定されている場合、画像機能のパラメータを追加
    if img_label_folder is not None:
        img_path = Path(img_label_folder)
        # 相対パスの場合は絶対パスに変換
        if not img_path.is_absolute():
            img_path = img_path.resolve()
        if img_path.exists() and img_path.is_dir():
            params["img_label_folder"] = str(img_path)
            # 画像モード（画像がない場合は自動的にテキスト表示）
            params["tick_label_mode"] = "image"
            params["tick_image_mode"] = "trailing"  # 画像がバーと一緒に移動するモード
        else:
            print(
                f"Warning: Image folder does not exist or is not a directory: {img_path}",
                file=sys.stderr,
            )

    return params


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


def generate_gif(
    df: pd.DataFrame,
    output_path: Path,
    cumulative: bool = False,
    img_label_folder: str | Path | None = None,
) -> None:
    """
    Bar Chart RaceのGIFを生成する。

    画像フォルダ指定時：
    - 画像がある絵文字 → 画像で表示
    - 画像がない絵文字 → Slack絵文字名でテキスト表示（例: +1, thumbsup）

    画像フォルダなし：すべての絵文字をSlack絵文字名でテキスト表示

    Args:
        df: 集計済みのpandas DataFrame（index: 月、columns: 絵文字名）
        output_path: 出力GIFファイルのパス
        cumulative: 累計モードの場合True
        img_label_folder: 画像ラベルフォルダのパス（Noneの場合はテキスト表示）
                         画像ファイルは「絵文字名.png」という形式で格納されている必要があります

    Raises:
        SystemExit: GIF生成に失敗した場合
    """
    if df.empty:
        print("Error in generate_gif: DataFrame is empty", file=sys.stderr)
        sys.exit(1)

    # 画像フォルダが指定されている場合、画像の有無を確認して統計情報を出力
    if img_label_folder is not None:
        img_path = Path(img_label_folder)
        # 相対パスの場合は絶対パスに変換
        if not img_path.is_absolute():
            img_path = img_path.resolve()

        if img_path.exists() and img_path.is_dir():
            # 画像フォルダ内の全ファイル名を取得（拡張子なし）
            image_files_by_stem: set[str] = {
                f.stem for f in img_path.iterdir() if f.is_file() and f.suffix == ".png"
            }

            images_found = []
            images_missing = []

            for col in df.columns:
                if col in image_files_by_stem:
                    images_found.append(col)
                else:
                    images_missing.append(col)

            # 統計情報を出力
            if images_found:
                print(
                    f"Info: {len(images_found)} emojis will be displayed as images",
                    file=sys.stderr,
                )

            if images_missing:
                print(
                    f"Info: {len(images_missing)} emojis will be displayed as text: "
                    f"{', '.join(images_missing[:10])}{'...' if len(images_missing) > 10 else ''}",
                    file=sys.stderr,
                )
        else:
            print(
                f"Warning: Image folder does not exist or is not a directory: {img_path}",
                file=sys.stderr,
            )
    else:
        print(
            f"Info: All {len(df.columns)} emojis will be displayed as text",
            file=sys.stderr,
        )

    # フォント設定を適用
    configure_fonts()

    params = configure_chart_params(cumulative, img_label_folder)

    try:
        bcr.bar_chart_race(
            df=df,
            filename=str(output_path),
            **params,
        )
    except Exception as e:
        import traceback

        print(f"Error in generate_gif: Failed to generate GIF: {e}", file=sys.stderr)
        print("Full traceback:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        print("Note: Make sure ffmpeg is installed if you see encoding errors.", file=sys.stderr)
        sys.exit(1)
