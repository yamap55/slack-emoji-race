"""メインエントリーポイント。"""

import argparse
import sys
from pathlib import Path

from logging_config import setup_logging
from slack_emoji_race.chart_generator import generate_gif
from slack_emoji_race.dataframe_builder import build_dataframe
from slack_emoji_race.reaction_aggregator import aggregate_reactions

setup_logging()

DEFAULT_OUTPUT_FILENAME = "slack_emoji_reactions_barchart_race.gif"


def parse_args() -> argparse.Namespace:
    """
    コマンドライン引数を解析する。

    Returns:
        解析された引数のNamespace
    """
    parser = argparse.ArgumentParser(
        description="Slack絵文字リアクションのBar Chart Raceアニメーションを生成します。"
    )
    parser.add_argument(
        "export_dir",
        type=str,
        help="Slackエクスポートを展開したディレクトリのパス",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=DEFAULT_OUTPUT_FILENAME,
        help=f"出力GIFファイル名（デフォルト: {DEFAULT_OUTPUT_FILENAME}）",
    )

    return parser.parse_args()


def main() -> None:
    """メイン処理。"""
    args = parse_args()

    export_dir = Path(args.export_dir)
    if not export_dir.exists():
        print(f"Error in main: Export directory does not exist: {export_dir}", file=sys.stderr)
        sys.exit(1)

    if not export_dir.is_dir():
        print(f"Error in main: Path is not a directory: {export_dir}", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.output)

    # リアクションを集計
    aggregated_data = aggregate_reactions(export_dir)

    if not aggregated_data:
        print("Error in main: No reactions found in export data", file=sys.stderr)
        sys.exit(1)

    # DataFrameを構築
    df = build_dataframe(aggregated_data)

    # GIFを生成
    generate_gif(df, output_path)

    print(f"Bar Chart Race GIF generated: {output_path}")


if __name__ == "__main__":
    main()
