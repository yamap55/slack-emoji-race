"""Slackエクスポートディレクトリの読み込みモジュール。"""

import json
import sys
from collections.abc import Iterator
from pathlib import Path


def find_channel_directories(export_dir: Path) -> list[Path]:
    """
    エクスポートディレクトリ内のチャンネルディレクトリを列挙する。

    Args:
        export_dir: Slackエクスポートのルートディレクトリ

    Returns:
        チャンネルディレクトリのリスト

    Raises:
        SystemExit: ディレクトリが存在しない、または読み取り不可の場合
    """
    if not export_dir.exists():
        msg = f"Error in find_channel_directories: Directory does not exist: {export_dir}"
        print(msg, file=sys.stderr)
        sys.exit(1)

    if not export_dir.is_dir():
        msg = f"Error in find_channel_directories: Path is not a directory: {export_dir}"
        print(msg, file=sys.stderr)
        sys.exit(1)

    channel_dirs = [d for d in export_dir.iterdir() if d.is_dir()]
    return sorted(channel_dirs)


def find_json_files(channel_dir: Path) -> list[Path]:
    """
    チャンネルディレクトリ内のJSONファイルを日付順に列挙する。

    Args:
        channel_dir: チャンネルディレクトリ

    Returns:
        JSONファイルのパスのリスト（日付順）

    Raises:
        SystemExit: ディレクトリが存在しない、または読み取り不可の場合
    """
    if not channel_dir.exists():
        print(f"Error in find_json_files: Directory does not exist: {channel_dir}", file=sys.stderr)
        sys.exit(1)

    if not channel_dir.is_dir():
        print(f"Error in find_json_files: Path is not a directory: {channel_dir}", file=sys.stderr)
        sys.exit(1)

    json_files = [f for f in channel_dir.iterdir() if f.is_file() and f.suffix == ".json"]
    return sorted(json_files)


def load_json_file(json_path: Path) -> list[dict]:
    """
    JSONファイルを読み込み、パースする。

    Args:
        json_path: JSONファイルのパス

    Returns:
        パースされたJSONデータ（メッセージのリスト）

    Raises:
        SystemExit: ファイルが存在しない、読み取り不可、またはJSONパースエラーの場合
    """
    if not json_path.exists():
        print(f"Error in load_json_file: File does not exist: {json_path}", file=sys.stderr)
        sys.exit(1)

    try:
        with json_path.open(encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        msg = f"Error in load_json_file: Failed to parse JSON file {json_path}: {e}"
        print(msg, file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"Error in load_json_file: Failed to read file {json_path}: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(data, list):
        msg = f"Error in load_json_file: JSON file {json_path} does not contain a list"
        print(msg, file=sys.stderr)
        sys.exit(1)

    return data


def load_all_messages(export_dir: Path) -> Iterator[dict]:
    """
    エクスポートディレクトリ内の全メッセージを順次読み込むジェネレータ。

    Args:
        export_dir: Slackエクスポートのルートディレクトリ

    Yields:
        各メッセージの辞書

    Raises:
        SystemExit: ディレクトリが存在しない、または読み取り不可の場合
    """
    channel_dirs = find_channel_directories(export_dir)

    for channel_dir in channel_dirs:
        json_files = find_json_files(channel_dir)

        for json_file in json_files:
            messages = load_json_file(json_file)
            yield from messages
