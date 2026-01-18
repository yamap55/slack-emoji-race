# Slack 絵文字リアクション Bar Chart Race

Slack ワークスペースの標準エクスポートを入力として、「絵文字リアクションの使用回数ランキング」が時間とともに変化する **Bar Chart Race 形式の GIF アニメーション** を生成するツールです。

## 概要

- Slack の標準エクスポート（Standard Export）を入力として受け取る
- メッセージのリアクション（絵文字）の使用回数を月別に集計
- 各月の TOP20 絵文字を Bar Chart Race 形式で可視化
- GIF アニメーションとして出力

## 主な機能

- **リアクションのみを対象**: メッセージ本文中の絵文字はカウントしません
- **月別集計**: 各月ごとに 0 リセットで集計（累計ではありません）
- **全チャンネル対応**: エクスポートに含まれるすべてのチャンネルを対象
- **標準・カスタム絵文字対応**: 両方に対応（カスタム絵文字は名前文字列として扱います）

## 入力データ

### Slack 標準エクスポート

- Slack の標準エクスポート ZIP を展開したディレクトリを入力として受け取ります
- ディレクトリ構造例：
  ```
  export/
  ├── general/
  │   ├── 2025-01-01.json
  │   ├── 2025-01-02.json
  │   └── ...
  ├── random/
  │   ├── 2025-01-01.json
  │   └── ...
  └── ...
  ```

### JSON ファイルの構造

各 JSON ファイルは以下のような構造を想定しています：

```json
[
  {
    "type": "message",
    "text": "hello :saikou:",
    "user": "U123456",
    "ts": "1730486400.000000",
    "reactions": [
      {
        "name": "saikou",
        "users": ["U123", "U456"],
        "count": 2
      },
      {
        "name": "thumbsup",
        "users": ["U789"],
        "count": 1
      }
    ]
  }
]
```

## 出力

- **メイン出力**: GIF アニメーションファイル（例: `slack_emoji_reactions_barchart_race.gif`）
- **オプション出力**:
  - 集計済み DataFrame の CSV（例: `emoji_reaction_counts_monthly.csv`）
  - 集計結果 JSON

## 集計仕様

### カウント方法

- 各メッセージの `reactions` 配列を参照
- `name` を絵文字の識別子として使用
- `count` の値をそのまま使用回数として加算
- メッセージの `ts`（epoch 秒）から年月（`YYYY-MM`）を算出して集計

### 時間軸

- タイムゾーン: UTC として扱います
- 集計単位: 月別（`YYYY-MM`）
- 集計ロジック:
  - **デフォルト（月別集計）**: 月ごとに 0 リセット（当該月の使用回数のみ）
  - **累計集計モード（`--cumulative`）**: 過去からの累計使用回数を表示

### ランキング

- 各月の TOP20 絵文字を表示
- 20 種類未満の場合は存在する分だけ表示

## 使用ライブラリ

- `pandas`: データ処理・集計
- `bar_chart_race`: Bar Chart Race アニメーション生成
- `matplotlib`: グラフ描画
- `ffmpeg`: 動画生成（環境依存）

## 環境詳細

- Python : 3.14

### 事前準備

- Docker インストール
- VS Code インストール
- VS Code の拡張機能「Remote - Containers」インストール
  - https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers
- 本リポジトリの clone
- ssh-agent の設定
  - https://code.visualstudio.com/docs/devcontainers/containers#_using-a-credential-helper

### 開発手順

1. VS Code 起動
2. 左下のアイコンクリック
3. 「Dev Containers: Reopen in Container」クリック
4. しばらく待つ
   - 初回の場合コンテナー image の取得や作成が行われる
5. 起動したら開発可能
   - 初回起動時は `uv sync` を実行してください

## 使用方法

### 基本的な使い方

```bash
# Slack エクスポートを展開したディレクトリを指定して実行
uv run python main.py /path/to/slack/export
```

### 起動オプション

#### 必須引数

- `export_dir`: Slack エクスポートを展開したディレクトリのパス

#### オプション引数

- `-o, --output <ファイル名>`: 出力 GIF ファイル名を指定（デフォルト: `slack_emoji_reactions_barchart_race.gif`）
- `--cumulative`: 累計集計モードを使用（デフォルト: 月別集計。各月で 0 リセット）

### 使用例

```bash
# 基本的な実行（デフォルトの出力ファイル名を使用）
uv run python main.py /path/to/slack/export

# 出力ファイル名を指定
uv run python main.py /path/to/slack/export -o my_output.gif

# 累計集計モードで実行
uv run python main.py /path/to/slack/export --cumulative

# 出力ファイル名を指定して累計集計モードで実行
uv run python main.py /path/to/slack/export -o cumulative_race.gif --cumulative
```

## NOTE

- 実行
  - `uv run python main.py <export_dir> [オプション]`
  - 例: `uv run python main.py /path/to/slack/export`
- ユニットテスト
  - `uv run python -m pytest`
    - `uvx pytest` の設定もしているが、uv 環境で実装されないため、上記コマンドで実行する
- lint
  - `uvx ruff check`
  - `uvx ruff check --fix`
- format
  - `uvx ruff format`
  - `uvx ruff format --check`
- 本番での依存ライブラリインストール
  - `uv sync --no-dev`

### 主な仕様の要点

- **対象**: メッセージのリアクションのみ（本文中の絵文字は無視）
- **絵文字**: 標準＋カスタム。カスタムは名前文字列として扱い、画像は扱わない
- **集計**: 月別、月ごとに 0 リセット
- **ランキング**: 各月の TOP20 絵文字
- **グラフ**: 横向きバー、ラベルは絵文字名、フレームごとに年月（`YYYY-MM`）を表示
