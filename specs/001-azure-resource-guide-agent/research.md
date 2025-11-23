# Phase 0 Research: Azure Resource Guide Agent

**Feature**: ../spec.md
**Date**: 2025-11-23

## Decisions

### 1. 言語とランタイム
- **Decision**: Python 3.10+ を採用する。
- **Rationale**: ユーザー指定の要件であり、Microsoft Agent Framework (Python) や GitHub Models のクライアントも Python サポートが充実しているため。Linux 上での CLI 実行とも相性が良い。
- **Alternatives considered**: Node.js / TypeScript（同様に MCP 連携しやすいが、ユーザー指定が Python であるため採用せず）。

### 2. エージェントフレームワーク
- **Decision**: Microsoft Agent Framework (Python) を利用してエージェントを構築する。
- **Rationale**: ユーザー指定のフレームワークであり、ツール呼び出し・会話管理・モデル接続などをまとめて扱える。将来の Web UI 連携や複雑なエージェント構成にも拡張しやすい。
- **Alternatives considered**: LangChain, Semantic Kernel などの他フレームワークは検討対象になり得るが、本プロジェクトでは要件に沿って Microsoft Agent Framework にフォーカスする。

### 3. モデルとエンドポイント
- **Decision**: GitHub Models の gpt-4o / gpt-4.1 を OpenAI 互換エンドポイントとして利用する。
- **Rationale**: ユーザー指定の候補であり、既存の OpenAI 互換クライアントや Microsoft Agent Framework から接続しやすい。日本語対応も十分であり、Azure リソース名や ID を含むテキスト処理にも適する。
- **Alternatives considered**: Azure OpenAI Service のモデルや他プロバイダを利用する選択肢もあるが、本リポジトリのサンプルとしては GitHub Models を前提とする。

### 4. Azure MCP Server との連携方式
- **Decision**: Azure MCP Server を `npx -y @azure/mcp@latest server start` で起動し、エージェント側では MCP クライアントとして接続する。
- **Rationale**: MCP プロトコルにより、Azure リソースへの読み取り専用アクセスを標準化されたインターフェースで行える。`npx` での起動により、追加インストールなしで試しやすい。
- **Alternatives considered**: 直接 Azure SDK や Azure CLI を呼び出す構成もあり得るが、本プロジェクトでは「Azure MCP Server を経由して調査する」という要件に従う。

### 5. 永続ストレージの扱い
- **Decision**: 初期バージョンでは永続ストレージは利用しない（N/A）。
- **Rationale**: 要件上、Azure リソースの構成やエラー状況をその場で確認できればよく、履歴や設定の永続化は必須ではない。シンプルさを優先し、状態はプロセス内に限定する。
- **Alternatives considered**: 設定ファイルや SQLite / ファイルベースのキャッシュを使う案もあるが、初期スコープでは不要と判断。

### 6. インターフェース形態（CLI / main.py / 将来の Web UI）
- **Decision**: 現時点では CLI とシンプルな `main.py` からの起動に対応し、将来的に Web UI やフロントエンドを追加できるように内部構造をパッケージ化する。
- **Rationale**: 開発者・SRE 向けツールとしてはローカル CLI が最も手軽であり、かつ Python パッケージとして切り出しておけば後から HTTP API や Web UI を追加しやすい。
- **Alternatives considered**: 初期から Web UI を持つ SPA + API 構成にする案もあるが、スコープが広がりすぎるため、まずは CLI ベースに集中する。

### 7. テスト戦略
- **Decision**: pytest を用いて、ユニットテストと軽量なインテグレーションテスト（MCP クライアントのモックを含む）を実装する。
- **Rationale**: Python プロジェクトで一般的であり、CI との連携も容易。CLI レベルの動作検証も pytest で十分にカバー可能。
- **Alternatives considered**: unittest など標準ライブラリベースのテストもあるが、記述性とエコシステムの観点から pytest を優先。

## Open Questions

現時点で仕様上の [NEEDS CLARIFICATION] は解消済みであり、Phase 1 の設計に進むにあたって特筆すべき未決事項はない。
