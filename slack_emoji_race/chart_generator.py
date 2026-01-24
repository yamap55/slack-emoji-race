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
        "period_label": {"x": 0.99, "y": 0.99, "ha": "right", "va": "top"},
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
            params["tick_label_mode"] = "image"  # 'image', 'mixed', またはデフォルトのテキスト
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

    Args:
        df: 集計済みのpandas DataFrame（index: 月、columns: 絵文字名）
        output_path: 出力GIFファイルのパス
        cumulative: 累計モードの場合True
        img_label_folder: 画像ラベルフォルダのパス（Noneの場合は画像を使用しない）
                         画像ファイルは「絵文字名.拡張子」という形式で格納されている必要があります

    Raises:
        SystemExit: GIF生成に失敗した場合
    """
    if df.empty:
        print("Error in generate_gif: DataFrame is empty", file=sys.stderr)
        sys.exit(1)

    # 画像フォルダが指定されている場合、画像ファイルが存在する列のみを残す
    if img_label_folder is not None:
        img_path = Path(img_label_folder)
        # 相対パスの場合は絶対パスに変換
        if not img_path.is_absolute():
            img_path = img_path.resolve()

        if img_path.exists() and img_path.is_dir():
            # 画像ファイルが存在する列をフィルタリング
            # フォーク版のget_image_name関数は拡張子がない場合に.pngを追加するため、
            # 事前にimage_converter.pyで変換済みの.pngファイルが存在することを前提とする
            available_columns = []
            missing_images = []

            # 画像フォルダ内の全ファイル名を取得（拡張子込み）
            # stem（拡張子なし）をキーとして、実際のファイル名（拡張子込み）を値として保存
            image_files_by_stem: dict[str, str] = {
                f.stem: f.name for f in img_path.iterdir() if f.is_file()
            }

            for col in df.columns:
                # 列名（絵文字名、拡張子なし）に対応するファイルを検索
                if col in image_files_by_stem:
                    available_columns.append(col)
                else:
                    missing_images.append(col)

            if missing_images:
                print(
                    f"Warning: Image files not found for {len(missing_images)} emojis: {', '.join(missing_images[:10])}{'...' if len(missing_images) > 10 else ''}",
                    file=sys.stderr,
                )
                print(
                    f"These emojis will be excluded from the chart.",
                    file=sys.stderr,
                )

            if available_columns:
                # フォーク版のget_image_name関数は拡張子がない場合に.pngを追加するため、
                # 実際のファイル名に対応する.pngファイルが存在することを確認
                # （事前にimage_converter.pyで変換済みであることを想定）
                missing_png_files = []

                for col in available_columns:
                    png_filename = f"{col}.png"
                    png_file_path = img_path / png_filename

                    if not png_file_path.exists():
                        missing_png_files.append(col)

                if missing_png_files:
                    print(
                        f"Warning: PNG files not found for {len(missing_png_files)} emojis. "
                        f"Please run image_converter.py first to convert images.",
                        file=sys.stderr,
                    )
                    print(
                        f"Missing files: {', '.join(missing_png_files[:10])}{'...' if len(missing_png_files) > 10 else ''}",
                        file=sys.stderr,
                    )
                    # 画像ファイルが見つからない列を除外
                    available_columns = [
                        col for col in available_columns if col not in missing_png_files
                    ]

                if not available_columns:
                    print(
                        "Error: No PNG files found. Please run image_converter.py first.",
                        file=sys.stderr,
                    )
                    sys.exit(1)

                df_filtered = df[available_columns]
                df = df_filtered  # type: ignore[assignment]
            else:
                print(
                    "Warning: No image files found. Disabling image label feature.",
                    file=sys.stderr,
                )
                img_label_folder = None

            if df.empty:
                print(
                    "Error in generate_gif: No columns with image files remaining", file=sys.stderr
                )
                sys.exit(1)

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
