# Feature Specification: Azure Resource Guide Agent

**Feature Branch**: `001-azure-resource-guide-agent`
**Created**: 2025-11-23
**Status**: Draft
**Input**: User description: "プロダクト名: Azure Resource Guide Agent / 目的: Azure MCP Server を経由して Azure サブスクリプション内のリソースを自然言語で調査できるようにする / 主なユーザー: Azure を扱うアプリ開発者・SRE・インフラ担当 / 主なユースケース: サブスクリプション内のリソースグループ一覧、特定リソースグループ内のストレージアカウント一覧、Log Analytics を使ったエラー調査 / 制約: 初期バージョンは読み取り専用、日本語対話、リソース名や ID は原文のまま表示 / 将来拡張: 次にやるべきトラブルシュートガイドの提案"

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.

  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - サブスクリプション全体のリソースグループを把握する (Priority: P1)

Azure を扱うアプリ開発者 / SRE / インフラ担当として、対象サブスクリプションに存在するリソースグループを日本語で問い合わせるだけで一覧できるようにしたい。これにより、ポータルを開いたりクエリを書かなくても、対話形式で全体構成を素早く把握できる。

**Why this priority**: どのリソースがどこにあるかを把握することは、運用・トラブルシュート・新規構成検討の起点となるため、最も基本的かつ頻度の高いニーズである。

**Independent Test**: テストサブスクリプションに対して「このサブスクリプションのリソースグループ一覧を出して」と問い合わせ、期待した全リソースグループ名と概要が返るかどうかのみで独立して検証できる。

**Acceptance Scenarios**:

1. **Given** Azure MCP Server が対象サブスクリプションに接続されている状態、**When** ユーザーが日本語で「このサブスクリプションのリソースグループ一覧を出して」と問い合わせる、**Then** サブスクリプション内のすべてのリソースグループ名と、必要に応じて場所・タグなどの基本情報が一覧で返る。
2. **Given** サブスクリプション内にリソースグループが 1 件も存在しない状態、**When** ユーザーが同様の問い合わせを行う、**Then** 「リソースグループは存在しません」といった分かりやすいメッセージが返り、エラーにはならない。

---

### User Story 2 - 特定リソースグループ内のストレージアカウントを把握する (Priority: P2)

Azure を扱うアプリ開発者 / SRE / インフラ担当として、特定のリソースグループ名を指定するだけで、その中に含まれるストレージアカウントを日本語で一覧してもらいたい。これにより、ストレージの利用状況確認や設定調査の対象を素早く絞り込める。

**Why this priority**: ストレージアカウントは多くのシステムで共通的に使われる基盤リソースであり、リソースグループ単位での把握ニーズが高いが、全体構成把握(P1)よりは優先度が一段下がるため P2 とする。

**Independent Test**: 特定のリソースグループに既知のストレージアカウントを複数作成し、「○○リソースグループのストレージアカウントを一覧して」と問い合わせるだけで、期待したアカウントがすべて正しく返るかどうかを検証できる。

**Acceptance Scenarios**:

1. **Given** 対象リソースグループ内に複数のストレージアカウントが存在する状態、**When** ユーザーが日本語で「<RG名> のストレージアカウントを一覧して」と問い合わせる、**Then** そのリソースグループ内のストレージアカウント名一覧が原文のまま返る。
2. **Given** 存在しないリソースグループ名を指定した状態、**When** ユーザーが同様の問い合わせを行う、**Then** 「指定されたリソースグループは見つかりませんでした」といった分かりやすいエラーメッセージが日本語で返る。

---

### User Story 3 - Log Analytics を用いたエラー状況の把握 (Priority: P3)

Azure を扱う SRE / インフラ担当として、対象サブスクリプションまたは特定ワークスペースに対して「最近のエラーを Log Analytics で調べて」などと問い合わせることで、代表的なエラー件数や概要を日本語で把握したい。

**Why this priority**: 運用・トラブルシュートにおいて重要だが、リソース構成の可視化(P1, P2)が先に整っていることが前提となるため、初期スコープでは P3 として段階的に取り込む。

**Independent Test**: 既知のエラーが一定件数発生しているテスト環境に対し、「直近 1 時間のエラーを Log Analytics で確認して」と問い合わせ、エラー数や代表的なメッセージが要約されて返るかを個別に検証できる。

**Acceptance Scenarios**:

1. **Given** Log Analytics ワークスペースにアプリケーションのエラーログが蓄積されている状態、**When** ユーザーが「直近 1 時間のエラーを Log Analytics で確認して」と日本語で問い合わせる、**Then** 主なエラー種別ごとの件数や代表的なメッセージが日本語で要約されて返る。
2. **Given** 指定期間にエラーが 1 件も存在しない状態、**When** ユーザーが同様の問い合わせを行う、**Then** 「指定期間にエラーは検出されませんでした」といったメッセージが日本語で返る。

---

[Add more user stories as needed, each with an assigned priority]

### Edge Cases

- サブスクリプションまたはリソースグループに対してアクセス権限が不足している場合、権限不足を示すメッセージを日本語で返し、Azure リソースの作成・削除・更新は一切行わないことを明示する。
- ユーザー入力があいまい（例: リソースグループ名の一部のみ、または解釈が複数ある自然言語）な場合、勝手に決め打ちせず、「どのリソースグループを指していますか？」などの追加質問で絞り込みを促す。
- 問い合わせに英語と日本語が混在している場合でも、日本語での対話を維持しつつ、Azure リソース名や ID は原文の表記のまま表示する。
- Azure 側の一時的なエラーやタイムアウトが発生した場合、再試行や時間をおいて再度実行するよう促す日本語メッセージを返し、詳細な技術スタック情報は露出しない。

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST allow users to request Azure リソース情報（リソースグループ、ストレージアカウント、Log Analytics からのエラー概要など）を日本語の自然言語で問い合わせできるようにする。
- **FR-002**: System MUST retrieve and list all resource groups within a given Azure subscription whenユーザーがサブスクリプション全体のリソースグループ一覧を問い合わせた場合、リソースグループ名や場所などの基本情報を含めて応答する。
- **FR-003**: System MUST retrieve and list all storage accounts within a specified resource group when ユーザーが対象リソースグループ名を指定してストレージアカウント一覧を問い合わせた場合に応答する。
- **FR-004**: System MUST query Log Analytics を用いて、指定された期間や条件に基づくエラーの件数や代表的なメッセージを集約し、日本語で要約した結果を返す。
- **FR-005**: System MUST keep all interactions with Azure resources read-only in the initial version, ensuring that no create, update, or delete operations are performed via thisエージェント。
- **FR-006**: System MUST respond to users in Japanese for all explanations,要約、エラーメッセージなどのテキスト部分については日本語で返しつつ、Azure リソース名や ID、SKU 名などは元の英数字表記のまま表示する。
- **FR-007**: System MUST handle cases where requested resources or workspaces do not exist by returning clear, user-friendly error messages in Japanese instead of低レベルな技術エラーをそのまま表示することは避ける。

*Example of marking unclear requirements:*

- **FR-008**: System MUST provide high-level troubleshooting guidance as 3〜5 ステップ程度の簡潔なガイド（代表的な原因候補の列挙と、「次に実行すべき確認手順」を箇条書きで示すレベル）を提示し、詳細な手順書レベルの長文ガイドや個別環境に依存する細かな操作指示までは含めない。

### Key Entities *(include if feature involves data)*

- **サブスクリプション**: Azure リソースの論理的なコンテナ。識別子、表示名、関連するテナント情報などを持つ。
- **リソースグループ**: サブスクリプション内のリソースをまとめる論理グループ。名前、場所、タグ、所属サブスクリプションなどの属性を持つ。
- **ストレージアカウント**: ストレージサービスを提供するリソース。アカウント名、種類、冗長化設定、場所、所属リソースグループなどの属性を持つ。
- **Log Analytics ワークスペース**: ログやメトリックを集約するワークスペース。ワークスペース名、場所、関連付けられたリソースなどを持つ。
- **エラーイベント**: Log Analytics に記録されるエラーの論理的単位。発生時刻、エラー種別、メッセージ概要、関連リソースなどの属性を持ち、集計・要約の対象となる。

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: 80% 以上のユーザーが、「このサブスクリプションのリソースグループ一覧を出して」といった問い合わせに対して、1 回の対話だけで目的の一覧情報を取得できる。
- **SC-002**: 代表的な問い合わせ（リソースグループ一覧、特定リソースグループのストレージアカウント一覧、直近 1 時間のエラー概要）に対して、平均応答時間が 10 秒以内である。
- **SC-003**: 初期ベータ利用ユーザーからのフィードバックにおいて、「構成の把握やエラー状況の確認が楽になった」と回答するユーザーが 70% 以上である。
- **SC-004**: 運用担当が Azure ポータルや手動クエリを用いて行っていたリソース構成確認・エラー状況確認の作業時間が、対象業務において 30% 以上削減されたと報告される。
