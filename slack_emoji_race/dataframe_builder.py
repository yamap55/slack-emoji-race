"""DataFrame構築モジュール。"""

import pandas as pd


def get_all_months(aggregated_data: dict[str, dict[str, int]]) -> list[str]:
    """
    集計データから全月のリストを取得し、時系列順にソートする。

    Args:
        aggregated_data: 月別集計辞書（{month: {emoji_name: count}}）

    Returns:
        月のリスト（時系列順）
    """
    months = list(aggregated_data.keys())
    return sorted(months)


def get_all_emojis(aggregated_data: dict[str, dict[str, int]]) -> set[str]:
    """
    集計データから全絵文字名のセットを取得する。

    Args:
        aggregated_data: 月別集計辞書（{month: {emoji_name: count}}）

    Returns:
        絵文字名のセット
    """
    emojis: set[str] = set()

    for month_data in aggregated_data.values():
        emojis.update(month_data.keys())

    return emojis


def _build_monthly_data(
    aggregated_data: dict[str, dict[str, int]], months: list[str], emojis: list[str]
) -> list[dict[str, int]]:
    """
    月別データを構築する（内部関数）。

    Args:
        aggregated_data: 月別集計辞書
        months: 月のリスト（時系列順）
        emojis: 絵文字名のリスト（ソート済み）

    Returns:
        データ行のリスト
    """
    data: list[dict[str, int]] = []

    for month in months:
        row: dict[str, int] = {}

        for emoji in emojis:
            row[emoji] = aggregated_data.get(month, {}).get(emoji, 0)

        data.append(row)

    return data


def _build_cumulative_data(
    aggregated_data: dict[str, dict[str, int]], months: list[str], emojis: list[str]
) -> list[dict[str, int]]:
    """
    累計データを構築する（内部関数）。

    Args:
        aggregated_data: 月別集計辞書
        months: 月のリスト（時系列順）
        emojis: 絵文字名のリスト（ソート済み）

    Returns:
        累計データ行のリスト
    """
    data: list[dict[str, int]] = []
    cumulative_counts: dict[str, int] = {}

    for month in months:
        row: dict[str, int] = {}

        for emoji in emojis:
            # 当月のカウントを取得
            monthly_count = aggregated_data.get(month, {}).get(emoji, 0)
            # 累計に加算
            cumulative_counts[emoji] = cumulative_counts.get(emoji, 0) + monthly_count
            row[emoji] = cumulative_counts[emoji]

        data.append(row)

    return data


def build_dataframe(aggregated_data: dict[str, dict[str, int]]) -> pd.DataFrame:
    """
    集計辞書からpandas DataFrameを構築する（月別集計）。

    Args:
        aggregated_data: 月別集計辞書（{month: {emoji_name: count}}）

    Returns:
        pandas DataFrame（index: 月、columns: 絵文字名、values: カウント）
    """
    months = get_all_months(aggregated_data)
    emojis = sorted(get_all_emojis(aggregated_data))

    data = _build_monthly_data(aggregated_data, months, emojis)

    # DataFrameを作成（インデックスをDatetimeIndexに変換）
    df = pd.DataFrame(data, index=pd.to_datetime(months))  # type: ignore

    return df


def build_cumulative_dataframe(aggregated_data: dict[str, dict[str, int]]) -> pd.DataFrame:
    """
    集計辞書から累計pandas DataFrameを構築する。

    Args:
        aggregated_data: 月別集計辞書（{month: {emoji_name: count}}）

    Returns:
        pandas DataFrame（index: 月、columns: 絵文字名、values: 累計カウント）
    """
    months = get_all_months(aggregated_data)
    emojis = sorted(get_all_emojis(aggregated_data))

    data = _build_cumulative_data(aggregated_data, months, emojis)

    # DataFrameを作成（インデックスをDatetimeIndexに変換）
    df = pd.DataFrame(data, index=pd.to_datetime(months))  # type: ignore

    return df
