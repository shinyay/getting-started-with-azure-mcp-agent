# Implementation Plan: Azure Resource Guide Agent

**Branch**: `001-azure-resource-guide-agent` | **Date**: 2025-11-23 | **Spec**: `specs/001-azure-resource-guide-agent/spec.md`
**Input**: Feature specification from `specs/001-azure-resource-guide-agent/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

このプランでは、Azure MCP Server を通じて Azure サブスクリプション内のリソース情報
（リソースグループ、ストレージアカウント、Log Analytics のエラー概要）を
日本語で問い合わせ・要約できる CLI ベースの AI エージェントを実装する。

実装は Python 3.10 + Microsoft Agent Framework(Python) を用い、
LLM には GitHub Models の gpt-4o / gpt-4.1 を利用する。
初期バージョンでは Azure リソースに対して完全に読み取り専用とし、
将来的に Web UI からも利用できるような構成を前提とする。


## Technical Context

**Language/Version**: Python 3.10+
**Primary Dependencies**: Microsoft Agent Framework (Python), GitHub Models (gpt-4o / gpt-4.1 互換クライアント), Azure MCP Server クライアント
**Storage**: N/A（初期バージョンでは永続ストレージ不要。必要に応じて将来拡張で設定保存などを検討）
**Testing**: pytest（ユニットテスト / インテグレーションテスト）
**Target Platform**: Linux server（ローカル or CI 環境上での CLI 実行を想定）
**Project Type**: single（Python パッケージ + CLI/`main.py`）
**Performance Goals**: 対話 1 リクエストあたりの処理時間が概ね 10 秒以内（Success Criteria と整合）。高スループットは必須ではなく、開発者個人〜小規模チームでの利用を主想定。
**Constraints**: 初期バージョンは Azure リソースに対して **完全読み取り専用**。Azure MCP Server を `npx -y @azure/mcp@latest server start` で起動し、MCP クライアントとして接続する構成とする。すべての対話は日本語だが、リソース名/ID は原文表記を維持。
**Scale/Scope**: 開発者/運用者向けのローカルツールとして、同時利用者数は少数（〜10 人程度）を想定。後に Web UI やフロントエンド追加でスケールさせる余地を残す。

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- 本リポジトリの `.specify/memory/constitution.md` はまだテンプレート状態であり、具体的な原則やゲートは定義されていない。
- したがって、現時点では「明示された憲法ルールに対する違反」は存在しないものとみなし、/speckit.plan の Phase 0・Phase 1 を進める。
- 今後、憲法が具体化された際には:
  - 言語・テスト・構成（単一 Python パッケージ + CLI）
  - 読み取り専用ポリシーと安全性
  - テスト優先（pytest による最低限のユニット/インテグレーションテスト）
 などが違反しないかを再評価する。

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
└── azure_mcp_agent/
    ├── __init__.py
    ├── config.py              # 設定・環境変数読み取り（モデル・エンドポイント・Azure MCP 接続情報など）
    ├── mcp_client.py          # Azure MCP Server へのクライアント接続ラッパー
    ├── prompts.py             # システムプロンプト／ツール定義など（Microsoft Agent Framework 用）
    ├── agent.py               # Microsoft Agent Framework ベースのエージェント本体
    ├── cli.py                 # CLI エントリポイント（`python -m azure_mcp_agent` / `azure-mcp-agent`）
    └── main.py                # シンプルな `python main.py` 実行用ラッパー（CLI 呼び出しを内部委譲）

tests/
└── azure_mcp_agent/
    ├── __init__.py
    ├── test_agent_basic.py    # リソースグループ一覧・ストレージアカウント一覧などの基本フロー（MCP をモック）
    ├── test_log_analytics.py  # Log Analytics エラー要約ロジックのテスト
    └── test_cli.py            # CLI レベルでの入出力・エラー処理のテスト
```

**Structure Decision**: 単一 Python パッケージ（`src/azure_mcp_agent`）構成とし、CLI/`main.py` からエージェントを起動する。将来的に Web UI やフロントエンドを追加する場合は、`web/` や `frontend/` ディレクトリを新設し、このパッケージをバックエンド SDK として再利用する。

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
