# Quickstart: Azure Resource Guide Agent

**Goal**: Azure MCP Server 経由で、Azure サブスクリプションのリソースを日本語で対話的に調査できるエージェントをローカルで動かす。

## 前提条件

- Python 3.10+ がインストール済み
- Node.js / npm がインストール済み（Azure MCP Server 起動用）
- Azure への認証がローカル環境で済んでいること（例: `az login` 済み）

## セットアップ（開発環境）

### 1. リポジトリを取得

```bash
git clone https://github.com/shinyay/getting-started-with-azure-mcp-agent.git
cd getting-started-with-azure-mcp-agent
```

### 2. Python 仮想環境を作成し、依存関係をインストール

```bash
python -m venv .venv
source .venv/bin/activate  # Windows の場合: .venv\Scripts\activate
pip install -e ".[dev]"
```

### 3. 環境変数の設定

以下の環境変数を設定してください。

#### GitHub Models を使用する場合（推奨）

```bash
export GITHUB_MODEL_NAME="gpt-4o"
export GITHUB_API_BASE="https://models.inference.ai.azure.com"
export GITHUB_API_KEY="your-github-token-here"
```

**GitHub Token の取得方法:**
1. GitHub の Settings → Developer settings → Personal access tokens
2. 新しいトークンを生成（GitHub Models API へのアクセス権限が必要。`repo` スコープは不要です）
3. 生成されたトークンを `GITHUB_API_KEY` に設定

#### Azure OpenAI を使用する場合

```bash
export AZURE_OPENAI_MODEL_NAME="your-deployment-name"
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_API_KEY="your-api-key-here"
export AZURE_OPENAI_API_VERSION="2024-02-15-preview"  # オプション
```

#### Azure MCP Server 設定（オプション）

デフォルトでは `npx -y @azure/mcp@latest server start --read-only` が使用されます。
カスタマイズする場合は以下の環境変数を設定してください:

```bash
export AZURE_MCP_COMMAND="npx"
export AZURE_MCP_ARGS="-y,@azure/mcp@latest,server,start,--read-only"  # カンマ区切り
```

#### その他の設定（オプション）

```bash
export MAX_COMPLETION_TOKENS="4096"  # デフォルト: 4096
export TEMPERATURE="0.7"              # デフォルト: 0.7
```

## Azure 認証の設定

Azure MCP Server が Azure リソースにアクセスできるよう、認証を設定してください:

```bash
az login
az account set --subscription <your-subscription-id>
```

## エージェントの起動

### 方法1: パッケージモジュールとして起動（推奨）

```bash
python -m azure_mcp_agent
```

### 方法2: エントリポイントスクリプトから起動

```bash
azure-mcp-agent
```

### 方法3: main.py から直接起動

```bash
python src/azure_mcp_agent/main.py
```

## 使い方

起動後、対話プロンプトが表示されます。日本語で質問を入力してください:

```
あなた: このサブスクリプションのリソースグループ一覧を出して
```

### 質問の例

**リソースグループ一覧:**
```
このサブスクリプションのリソースグループ一覧を出して
```

**ストレージアカウント一覧:**
```
<リソースグループ名> のストレージアカウントを一覧して
```

**Log Analytics エラー確認:**
```
直近1時間のエラーをLog Analyticsで確認して
```

### 終了方法

- `exit` または `quit` と入力
- Ctrl+C を押す
- Ctrl+D を押す

## 現在の実装状況（Phase 3 完了時点）

✅ **実装済み:**
- 設定管理（config.py）
- Azure MCP クライアント接続（mcp_client.py）
- 日本語プロンプト・システムインストラクション（prompts.py）
- エージェント本体（agent.py）
- 対話型 CLI（cli.py）
- メインエントリポイント（main.py）
- **User Story 1: リソースグループ一覧** ✨ NEW
  - 日本語での自然言語クエリに対応
  - 空のサブスクリプション・権限エラーのハンドリング
  - テストコード完備（test_agent_basic.py, test_cli.py）

⏳ **未実装（Phase 4-5 で対応予定）:**
- User Story 2: ストレージアカウント一覧の具体的な実装
- User Story 3: Log Analytics エラー要約の具体的な実装

## トラブルシューティング

### 環境変数が設定されていないエラー

```
設定エラー: 必須の環境変数が設定されていません: GITHUB_MODEL_NAME or AZURE_OPENAI_MODEL_NAME
```

→ 上記の「環境変数の設定」セクションを参照して、必要な環境変数を設定してください。

### MCP Server への接続エラー

```
接続エラー: Azure MCP Server への接続に失敗しました
```

→ 以下を確認してください:
1. Node.js / npm がインストールされている
2. Azure 認証が完了している（`az login`）
3. ネットワーク接続が正常

### Node.js が見つからないエラー

```
警告: MCP サーバーコマンド 'npx' が見つかりません。
```

→ Node.js をインストールしてください:
- https://nodejs.org/ からインストール
- または: `brew install node` (macOS) / `apt install nodejs npm` (Ubuntu)

## 期待される動作

- Azure MCP Server を通じて Azure サブスクリプションの情報にアクセス
- すべての回答は日本語で表示
- Azure リソース名や ID は原文のまま表示
- 読み取り専用の操作のみ（作成・更新・削除は行わない）

## 次のステップ

- Phase 3: User Story 1（リソースグループ一覧）の実装
- Phase 4: User Story 2（ストレージアカウント一覧）の実装
- Phase 5: User Story 3（Log Analytics エラー要約）の実装
- Phase 6: テストの追加とポリッシング
