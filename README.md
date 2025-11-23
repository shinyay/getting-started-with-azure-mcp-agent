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
pip install -e .
```

## Usage

1. Azure MCP Server を起動（別ターミナル）:

```bash
npx -y @azure/mcp@latest server start
```

2. エージェントを起動:

```bash
python -m azure_mcp_agent
# または
azure-mcp-agent
```

3. 日本語で問い合わせを行う:

- 例: `このサブスクリプションのリソースグループ一覧を出して`
- 例: `<RG名> のストレージアカウントを一覧して`
- 例: `直近 1 時間のエラーを Log Analytics で確認して`

## Development

テストを実行:

```bash
pytest
```

## References

- [Microsoft Agent Framework](https://github.com/microsoft/agent-framework)
- [Azure MCP Server](https://github.com/azure/mcp)
- [Spec Documentation](specs/001-azure-resource-guide-agent/spec.md)

## Licence

Released under the [MIT license](https://gist.githubusercontent.com/shinyay/56e54ee4c0e22db8211e05e70a63247e/raw/f3ac65a05ed8c8ea70b653875ccac0c6dbc10ba1/LICENSE)

## Author

- github: <https://github.com/shinyay>
- twitter: <https://twitter.com/yanashin18618>
- mastodon: <https://mastodon.social/@yanashin>
