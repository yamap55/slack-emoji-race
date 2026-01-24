# AGENTS.md

Slack 絵文字リアクションを Bar Chart Race GIF アニメーションとして可視化するツール。Slack 標準エクスポート（JSON）から月別リアクション集計を行い、TOP20 の推移をアニメーション化します。

## Setup commands

```bash
# 依存関係インストール（開発環境、テストツール含む）
uv sync

# 本番環境用（テストツール除外）
uv sync --no-dev
```

## Running the application

```bash
# 基本実行
uv run python main.py <export_dir>

# 出力ファイル名指定
uv run python main.py <export_dir> -o output.gif

# 累計集計モード
uv run python main.py <export_dir> --cumulative

# 画像ラベル使用
uv run python main.py <export_dir> --img-folder ./images

# 画像変換（画像ラベル機能の前準備）
uv run python -m slack_emoji_race.image_converter ./input_images -o ./output_images
```

## Testing

```bash
# 全テスト実行
uv run python -m pytest

# カバレッジ付き（デフォルト有効）
uv run python -m pytest --cov

# 特定のテストファイルのみ
uv run python -m pytest tests/slack_emoji_race/test_reaction_aggregator.py
```

**テスト構成**:
- `tests/fixtures/`: Slack エクスポート JSON フィクスチャ
- `tests/slack_emoji_race/`: 各モジュールのユニットテスト
- `tests/test_integration.py`: 統合テスト
- 新機能追加時は対応するテストを必ず追加
- 変更後は必ず `uv run python -m pytest` 実行

## Code style

- Python 3.11.14
- Google スタイルの docstring を全関数に記述
- 型ヒント必須（引数・戻り値）
- ダブルクォート使用
- 最大行長: 100 文字

```bash
# リント実行
uvx ruff check

# 自動修正
uvx ruff check --fix

# フォーマット
uvx ruff format

# フォーマットチェック
uvx ruff format --check
```

## Project structure

- `main.py`: エントリーポイント、CLI 引数解析
- `slack_emoji_race/export_loader.py`: Slack エクスポート JSON 読み込み
- `slack_emoji_race/reaction_aggregator.py`: リアクション集計、JST タイムスタンプ処理
- `slack_emoji_race/dataframe_builder.py`: pandas DataFrame 構築
- `slack_emoji_race/chart_generator.py`: bar_chart_race による GIF 生成
- `slack_emoji_race/image_converter.py`: 画像変換（RGBA PNG へ）
- `tests/`: ユニットテスト・統合テスト

## Key technical details

### タイムゾーン処理

- 全タイムスタンプは**日本時間（JST, UTC+9）**で処理
- `reaction_aggregator.py` の `JST` 定数と `parse_timestamp_to_month()` 関数で実装
- Slack の `ts` フィールド（epoch 秒）を JST の `YYYY-MM` に変換

### 絵文字名の正規化

- 肌色バリエーション（`::skin-tone-X`）を削除
- `normalize_emoji_name()` 関数: `thumbsup::skin-tone-2` → `thumbsup`

### Bar Chart Race ライブラリ

- フォーク版使用: `andresberejnoi/bar_chart_race@image_labels`
- 画像ラベル機能サポート
- パラメータ名がオリジナルと異なる場合あり（`bar_label_font`, `tick_label_font`）

### 画像ラベル機能

- 画像ファイル形式: **RGBA 形式の PNG**
- ファイル命名規則: `絵文字名.png`（拡張子なしの絵文字名が DataFrame 列名と一致）
- 事前に `image_converter.py` で変換必須
- 画像未発見の絵文字は自動除外（警告表示）

### エラーハンドリング

- `sys.stderr` にエラー出力
- `sys.exit(1)` で終了
- トレースバック含む詳細情報提供（`chart_generator.py` 参照）

## Common issues

### 日本語フォント不在

エラー: `Japanese font (Noto Sans CJK) not found`

```bash
# Docker環境
# .devcontainer/Dockerfile で fonts-noto-cjk インストール済みか確認

# ローカル環境
sudo apt install fonts-noto-cjk
```

### ffmpeg 不在

```bash
# Docker環境
# .devcontainer/Dockerfile で ffmpeg インストール済みか確認

# ローカル環境
sudo apt install ffmpeg
```

### 画像ラベル表示されない

```bash
# 1. 画像を RGBA PNG に変換
uv run python -m slack_emoji_race.image_converter ./input_images -o ./converted_images

# 2. 変換済みフォルダを指定
uv run python main.py ./export --img-folder ./converted_images

# 3. ログで画像検出状況を確認
```
