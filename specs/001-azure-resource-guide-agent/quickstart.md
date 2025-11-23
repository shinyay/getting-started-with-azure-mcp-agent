# Quickstart: Azure Resource Guide Agent

**Goal**: Azure MCP Server 経由で、Azure サブスクリプションのリソースを日本語で対話的に調査できるエージェントをローカルで動かす。

## 前提条件

- Python 3.10+ がインストール済み
- Node.js / npm がインストール済み（Azure MCP Server 起動用）
- Azure への認証がローカル環境で済んでいること（例: `az login` 済み）

## セットアップ（開発環境）

1. リポジトリを取得し、ブランチをチェックアウト:

   - `001-azure-resource-guide-agent` ブランチを利用

2. Python 仮想環境を作成し、依存関係をインストール:

   - `python -m venv .venv`
   - `.venv` を有効化し、`pip install -e .`（将来的に `pyproject.toml` / `setup.cfg` で依存を管理）

3. GitHub Models / モデルエンドポイントの設定:

   - 環境変数でモデル名やエンドポイント、トークンを設定（例: `GITHUB_MODEL_NAME`, `GITHUB_API_BASE`, `GITHUB_API_KEY` など）
   - 実際のキー名や読み方は `src/azure_mcp_agent/config.py` で統一的に扱う。

## Azure MCP Server の起動

1. 別ターミナルで Azure MCP Server を起動:

   - プロジェクトルートで `npx -y @azure/mcp@latest server start`

2. MCP Server が起動したら、エージェント側から MCP クライアントとして接続できるようにする。

## エージェントの起動

1. CLI から直接起動:

   - `python -m azure_mcp_agent` もしくは `azure-mcp-agent`（エントリポイントスクリプトが用意されている場合）

2. シンプルな `main.py` から起動:

   - プロジェクトルートで `python src/azure_mcp_agent/main.py`

3. 起動後、対話プロンプトが表示されたら、日本語で問い合わせを行う:

   - 例: `このサブスクリプションのリソースグループ一覧を出して`
   - 例: `<RG名> のストレージアカウントを一覧して`
   - 例: `直近 1 時間のエラーを Log Analytics で確認して`

## 期待される動作

- Azure MCP Server を通じて Azure サブスクリプションの情報にアクセスし、
  - リソースグループ一覧
  - 特定リソースグループ内のストレージアカウント一覧
  - Log Analytics を用いたエラー要約
  を取得する。
- すべての回答は日本語で行われるが、Azure リソース名や ID は原文のまま表示される。
- 初期バージョンでは Azure リソースの作成・更新・削除は一切行わず、読み取り専用の調査に限定される。

## 次のステップ

- テスト (`pytest`) を追加して、主要なユーザーストーリー（リソースグループ一覧、ストレージアカウント一覧、エラー要約）が満たされていることを自動検証する。
- 必要に応じて、将来の Web UI / フロントエンド向けに HTTP API レイヤや Web アプリを追加し、`src/azure_mcp_agent` パッケージを再利用する。
