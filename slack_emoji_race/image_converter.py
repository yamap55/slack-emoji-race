"""
画像ファイル変換モジュール。

画像フォルダ内の画像ファイルを、bar_chart_raceで使用可能な形式に変換します。
- RGB/RGBA形式の.pngファイルはそのままコピー
- その他の形式（.gif、.jpg、LA/Pモードなど）はRGBA形式の.pngに変換
"""

import shutil
import sys
from pathlib import Path

from PIL import Image


def convert_image_if_needed(source_path: Path, dest_path: Path) -> bool:
    """
    画像ファイルを必要に応じて変換する。

    Args:
        source_path: 元の画像ファイルのパス
        dest_path: 出力先のパス（.png拡張子）

    Returns:
        変換が必要だった場合True、そのままコピーした場合False
    """
    try:
        img = Image.open(source_path)
        source_ext = source_path.suffix.lower()

        # .pngファイルで、RGBまたはRGBA形式の場合はそのままコピー
        if source_ext == ".png" and img.mode in ("RGB", "RGBA"):
            shutil.copy2(source_path, dest_path)
            return False

        # それ以外の場合はRGBA形式に変換して保存
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGBA")
        else:
            # RGB形式の場合はRGBAに変換（アルファチャンネルを追加）
            if img.mode == "RGB":
                img = img.convert("RGBA")

        # .pngファイルとして保存
        img.save(dest_path, "PNG")
        return True

    except Exception as e:
        print(f"Error converting {source_path}: {e}", file=sys.stderr)
        raise


def convert_image_folder(source_folder: Path, output_folder: Path) -> None:
    """
    画像フォルダ内の画像ファイルを変換する。

    Args:
        source_folder: 元の画像フォルダのパス
        output_folder: 出力先フォルダのパス

    Raises:
        SystemExit: エラーが発生した場合
    """
    if not source_folder.exists():
        print(f"Error: Source folder does not exist: {source_folder}", file=sys.stderr)
        sys.exit(1)

    if not source_folder.is_dir():
        print(f"Error: Source path is not a directory: {source_folder}", file=sys.stderr)
        sys.exit(1)

    # 出力フォルダを作成
    output_folder.mkdir(parents=True, exist_ok=True)

    # 画像ファイルの拡張子リスト
    image_extensions = {".png", ".jpg", ".jpeg", ".gif", ".PNG", ".JPG", ".JPEG", ".GIF"}

    converted_count = 0
    copied_count = 0
    error_count = 0

    # 画像ファイルを処理
    for source_file in source_folder.iterdir():
        if not source_file.is_file():
            continue

        if source_file.suffix not in image_extensions:
            continue

        # 出力ファイル名は拡張子なしのベース名 + .png
        output_filename = f"{source_file.stem}.png"
        output_path = output_folder / output_filename

        try:
            converted = convert_image_if_needed(source_file, output_path)
            if converted:
                converted_count += 1
                print(f"Converted: {source_file.name} -> {output_filename}")
            else:
                copied_count += 1
                print(f"Copied: {source_file.name} -> {output_filename}")
        except Exception as e:
            error_count += 1
            print(f"Error processing {source_file.name}: {e}", file=sys.stderr)

    print("\nSummary:")
    print(f"  Converted: {converted_count}")
    print(f"  Copied: {copied_count}")
    print(f"  Errors: {error_count}")
    print(f"  Output folder: {output_folder}")


def main() -> None:
    """メイン処理。"""
    import argparse

    parser = argparse.ArgumentParser(
        description="画像フォルダ内の画像ファイルをbar_chart_raceで使用可能な形式に変換します。"
    )
    parser.add_argument(
        "source_folder",
        type=str,
        help="元の画像フォルダのパス",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        required=True,
        help="出力先フォルダのパス",
    )

    args = parser.parse_args()

    source_folder = Path(args.source_folder)
    output_folder = Path(args.output)

    convert_image_folder(source_folder, output_folder)
    print(f"\nImage conversion completed: {output_folder}")


if __name__ == "__main__":
    main()
