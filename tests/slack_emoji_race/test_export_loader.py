"""ExportLoaderモジュールのテスト。"""

import json
from pathlib import Path

import pytest

from slack_emoji_race.export_loader import (
    find_channel_directories,
    find_json_files,
    load_all_messages,
    load_json_file,
)


def test_find_channel_directories(tmp_path: Path) -> None:
    """find_channel_directoriesのテスト。"""
    # テスト用ディレクトリ構造を作成
    channel1 = tmp_path / "general"
    channel2 = tmp_path / "random"
    channel1.mkdir()
    channel2.mkdir()

    result = find_channel_directories(tmp_path)
    assert len(result) == 2
    assert channel1 in result
    assert channel2 in result


def test_find_channel_directories_nonexistent() -> None:
    """存在しないディレクトリの場合のテスト。"""
    nonexistent = Path("/nonexistent/directory/12345")
    with pytest.raises(SystemExit):
        find_channel_directories(nonexistent)


def test_find_json_files(tmp_path: Path) -> None:
    """find_json_filesのテスト。"""
    # テスト用JSONファイルを作成
    json1 = tmp_path / "2025-01-01.json"
    json2 = tmp_path / "2025-01-02.json"
    json1.write_text("[]")
    json2.write_text("[]")

    result = find_json_files(tmp_path)
    assert len(result) == 2
    assert json1 in result
    assert json2 in result
    # 日付順にソートされていることを確認
    assert result[0] == json1
    assert result[1] == json2


def test_find_json_files_nonexistent() -> None:
    """存在しないディレクトリの場合のテスト。"""
    nonexistent = Path("/nonexistent/directory/12345")
    with pytest.raises(SystemExit):
        find_json_files(nonexistent)


def test_load_json_file(tmp_path: Path) -> None:
    """load_json_fileのテスト。"""
    json_file = tmp_path / "test.json"
    test_data = [{"type": "message", "text": "test", "ts": "1234567890.000000"}]
    json_file.write_text(json.dumps(test_data), encoding="utf-8")

    result = load_json_file(json_file)
    assert result == test_data


def test_load_json_file_invalid_json(tmp_path: Path) -> None:
    """不正なJSONファイルの場合のテスト。"""
    json_file = tmp_path / "invalid.json"
    json_file.write_text("{ invalid json }", encoding="utf-8")

    with pytest.raises(SystemExit):
        load_json_file(json_file)


def test_load_json_file_not_list(tmp_path: Path) -> None:
    """リストでないJSONの場合のテスト。"""
    json_file = tmp_path / "not_list.json"
    json_file.write_text('{"key": "value"}', encoding="utf-8")

    with pytest.raises(SystemExit):
        load_json_file(json_file)


def test_load_all_messages(tmp_path: Path) -> None:
    """load_all_messagesのテスト。"""
    # テスト用ディレクトリ構造を作成
    fixtures_dir = Path(__file__).parent.parent / "fixtures"

    messages = list(load_all_messages(fixtures_dir))
    assert len(messages) > 0

    # 最初のメッセージが正しく読み込まれていることを確認
    first_message = messages[0]
    assert "type" in first_message
    assert "ts" in first_message
