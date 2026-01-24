"""統合テスト。"""

from pathlib import Path
from unittest.mock import patch

from slack_emoji_race.chart_generator import generate_gif
from slack_emoji_race.dataframe_builder import build_dataframe
from slack_emoji_race.reaction_aggregator import aggregate_reactions


def test_end_to_end(tmp_path: Path) -> None:
    """エンドツーエンドの統合テスト。"""
    fixtures_dir = Path(__file__).parent / "fixtures"

    # リアクションを集計
    aggregated_data = aggregate_reactions(fixtures_dir)

    # データが存在することを確認
    assert aggregated_data

    # DataFrameを構築
    df = build_dataframe(aggregated_data)

    # DataFrameが空でないことを確認
    assert not df.empty

    # GIF生成はスキップ（実際のファイル生成は時間がかかるため）
    # 必要に応じてコメントアウトを外してテスト
    # output_path = tmp_path / "test_output.gif"
    # generate_gif(df, output_path)
    # assert output_path.exists()


@patch("slack_emoji_race.chart_generator.bcr")
def test_end_to_end_with_image_folder(mock_bcr, tmp_path: Path) -> None:
    """画像フォルダ指定時の統合テスト（画像あり・なし混在）。"""
    fixtures_dir = Path(__file__).parent / "fixtures"

    # リアクションを集計
    aggregated_data = aggregate_reactions(fixtures_dir)

    # DataFrameを構築
    df = build_dataframe(aggregated_data)

    # 画像フォルダとファイルを作成（saikouのみ）
    img_folder = tmp_path / "images"
    img_folder.mkdir()
    (img_folder / "saikou.png").touch()

    # GIF生成（モック使用、画像フォルダ指定あり）
    output_path = tmp_path / "test_output.gif"
    generate_gif(df, output_path, cumulative=False, img_label_folder=str(img_folder))

    # bar_chart_raceが呼ばれたことを確認
    mock_bcr.bar_chart_race.assert_called_once()
    call_args = mock_bcr.bar_chart_race.call_args

    # imageモードが設定されていることを確認
    assert call_args.kwargs["tick_label_mode"] == "image"

    # DataFrameの列名は変換されずそのまま
    df_passed = call_args.kwargs["df"]
    columns = set(df_passed.columns)
    assert "saikou" in columns
    assert "thumbsup" in columns
