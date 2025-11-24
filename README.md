# Azure Resource Guide Agent

## Description

Azure Resource Guide Agent は、Azure MCP Server を経由して Azure サブスクリプション内のリソースを日本語の自然言語で調査できる CLI ベースの AI エージェントです。

このエージェントを使用すると、Azure ポータルを開いたりクエリを書いたりすることなく、対話形式で以下のような情報を素早く取得できます：

- サブスクリプション内のリソースグループ一覧
- 特定リソースグループ内のストレージアカウント一覧
- Log Analytics を用いたエラー状況の把握

## Features

- **日本語対話**: すべての問い合わせと回答が日本語で行われます（Azure リソース名や ID は原文のまま表示）
- **読み取り専用**: 初期バージョンでは Azure リソースに対して完全に読み取り専用で、安全に利用できます
- **自然言語クエリ**: 複雑なクエリを書く必要がなく、自然な日本語で質問できます
- **Azure MCP Server 連携**: Azure MCP Server を通じて Azure リソース情報にアクセスします

## Requirements

- Python 3.10 以上
- Node.js / npm（Azure MCP Server 起動用）
- Azure への認証が設定済みであること（例: `az login` 実行済み）

## Installation

1. リポジトリをクローン:

```bash
git clone https://github.com/shinyay/getting-started-with-azure-mcp-agent.git
cd getting-started-with-azure-mcp-agent
```

2. Python 仮想環境を作成し、依存関係をインストール:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows の場合: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Quick Start

詳細な使用方法と例については、**[Quickstart ガイド](specs/001-azure-resource-guide-agent/quickstart.md)** を参照してください。

### 基本的な使い方

1. 環境変数を設定:
```bash
export GITHUB_MODEL_NAME="gpt-4o"
export GITHUB_API_KEY="your-github-token-here"
export GITHUB_API_BASE="https://models.inference.ai.azure.com"
```

2. Azure 認証:
```bash
az login
az account set --subscription <your-subscription-id>
```

3. エージェントを起動:
```bash
azure-mcp-agent
# または
python -m azure_mcp_agent
```

4. 日本語で問い合わせを行う:
```
あなた: このサブスクリプションのリソースグループ一覧を出して
あなた: rg-app-core のストレージアカウントを一覧して
あなた: 直近1時間のエラーをLog Analyticsで確認して
```

**📖 詳細な使用例と期待される出力については [Quickstart](specs/001-azure-resource-guide-agent/quickstart.md) を参照してください。**

## Documentation

- **[Quickstart ガイド](specs/001-azure-resource-guide-agent/quickstart.md)** - セットアップと使用例
- **[プロダクト仕様](specs/001-azure-resource-guide-agent/spec.md)** - 機能要件とユーザーストーリー
- **[実装プラン](specs/001-azure-resource-guide-agent/plan.md)** - アーキテクチャと設計判断
- **[タスク一覧](specs/001-azure-resource-guide-agent/tasks.md)** - 開発タスクとフェーズ

## Development

### テストを実行

すべてのテストを実行:
```bash
pytest
```

特定のテストファイルのみ実行:
```bash
pytest tests/azure_mcp_agent/test_agent_basic.py -v
```

### ログレベルの設定

デバッグログを有効化:
```bash
export AZURE_MCP_AGENT_LOG_LEVEL=DEBUG
python -m azure_mcp_agent
```

### コード構成

```
src/azure_mcp_agent/
├── __init__.py          # パッケージ初期化
├── __main__.py          # python -m azure_mcp_agent エントリポイント
├── agent.py             # エージェント本体（ChatAgent の作成）
├── cli.py               # 対話型 CLI REPL
├── config.py            # 設定管理（環境変数からの読み込み）
├── main.py              # メインエントリポイント
├── mcp_client.py        # Azure MCP Server クライアント
└── prompts.py           # システムプロンプトとメッセージテンプレート
```

## References

- [Microsoft Agent Framework](https://github.com/microsoft/agent-framework)
- [Azure MCP Server](https://github.com/azure/mcp)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)

## Licence

Released under the [MIT license](https://gist.githubusercontent.com/shinyay/56e54ee4c0e22db8211e05e70a63247e/raw/f3ac65a05ed8c8ea70b653875ccac0c6dbc10ba1/LICENSE)

## Author

- github: <https://github.com/shinyay>
- twitter: <https://twitter.com/yanashin18618>
- mastodon: <https://mastodon.social/@yanashin>
