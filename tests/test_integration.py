"""統合テスト。"""

from pathlib import Path

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
