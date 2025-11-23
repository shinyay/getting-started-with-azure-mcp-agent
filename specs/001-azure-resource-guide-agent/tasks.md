---

description: "Tasks for implementing Azure Resource Guide Agent"

---

# Tasks: Azure Resource Guide Agent

**Input**: Design documents from `/specs/001-azure-resource-guide-agent/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/, quickstart.md

**Tests**: This feature explicitly requires pytest-based tests for each user story (CLI, agent behavior, Log Analytics summarization).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create Python project scaffolding with src/azure_mcp_agent and tests/azure_mcp_agent packages
- [ ] T002 Initialize packaging metadata and dependencies in pyproject.toml at repository root
- [ ] T003 [P] Configure basic pytest setup in tests/azure_mcp_agent/__init__.py and root pytest.ini
- [ ] T004 [P] Add .gitignore and basic repo hygiene files (README.md, LICENSE) at repository root

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Implement configuration loader in src/azure_mcp_agent/config.py for model and MCP settings
- [ ] T006 [P] Implement Azure MCP client wrapper in src/azure_mcp_agent/mcp_client.py (connection, basic calls)
- [ ] T007 [P] Define base prompts and system instructions in src/azure_mcp_agent/prompts.py (Japanese responses, read-only policy)
- [ ] T008 Implement core Agent class using Microsoft Agent Framework in src/azure_mcp_agent/agent.py
- [ ] T009 Implement CLI entry module in src/azure_mcp_agent/cli.py for interactive REPL over stdin/stdout
- [ ] T010 [P] Implement simple main entrypoint in src/azure_mcp_agent/main.py delegating to cli.main()
- [ ] T011 Configure environment-based settings documentation in specs/001-azure-resource-guide-agent/quickstart.md

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - サブスクリプション全体のリソースグループを把握する (Priority: P1) 🎯 MVP

**Goal**: ユーザーが日本語で問い合わせるだけで、対象サブスクリプションのリソースグループ一覧（名前や場所など）を取得できるようにする。

**Independent Test**: テストサブスクリプションに対して CLI 経由で「このサブスクリプションのリソースグループ一覧を出して」と問い合わせたとき、既知のリソースグループがすべて日本語の説明付きで返ることを pytest から自動検証できる。

### Tests for User Story 1 ⚠️

- [ ] T012 [P] [US1] Add basic agent behavior tests for resource group listing in tests/azure_mcp_agent/test_agent_basic.py
- [ ] T013 [P] [US1] Add CLI-level integration tests for resource group listing in tests/azure_mcp_agent/test_cli.py

### Implementation for User Story 1

- [ ] T014 [P] [US1] Implement MCP call for listing resource groups in src/azure_mcp_agent/mcp_client.py
- [ ] T015 [P] [US1] Implement agent intent handling for "リソースグループ一覧" queries in src/azure_mcp_agent/agent.py
- [ ] T016 [US1] Implement Japanese formatting and summarization of resource group list in src/azure_mcp_agent/agent.py
- [ ] T017 [US1] Wire CLI command flow for resource group listing queries in src/azure_mcp_agent/cli.py
- [ ] T018 [US1] Add error handling for empty or inaccessible subscriptions in src/azure_mcp_agent/agent.py

**Checkpoint**: User Story 1 should be fully functional and testable independently (MVP scope)

---

## Phase 4: User Story 2 - 特定リソースグループ内のストレージアカウントを把握する (Priority: P2)

**Goal**: 特定リソースグループ名を指定した日本語問い合わせに対して、その中のストレージアカウント一覧を原文名のまま返せるようにする。

**Independent Test**: 既知のストレージアカウントを含むテスト用リソースグループに対し、「<RG名> のストレージアカウントを一覧して」と CLI から問い合わせたとき、対象アカウントがすべて返ることを pytest から自動検証できる。

### Tests for User Story 2 ⚠️

- [ ] T019 [P] [US2] Add agent tests for storage account listing behavior in tests/azure_mcp_agent/test_agent_basic.py
- [ ] T020 [P] [US2] Add CLI tests for storage account listing queries in tests/azure_mcp_agent/test_cli.py

### Implementation for User Story 2

- [ ] T021 [P] [US2] Implement MCP call for listing storage accounts in a resource group in src/azure_mcp_agent/mcp_client.py
- [ ] T022 [P] [US2] Implement agent intent handling for "<RG名> のストレージアカウント" queries in src/azure_mcp_agent/agent.py
- [ ] T023 [US2] Implement validation and disambiguation for resource group names in src/azure_mcp_agent/agent.py
- [ ] T024 [US2] Implement CLI-side argument/utterance parsing for RG-specific queries in src/azure_mcp_agent/cli.py
- [ ] T025 [US2] Implement Japanese error messages for missing or unknown resource groups in src/azure_mcp_agent/agent.py

**Checkpoint**: User Stories 1 and 2 should both work independently and pass their tests

---

## Phase 5: User Story 3 - Log Analytics を用いたエラー状況の把握 (Priority: P3)

**Goal**: Log Analytics ワークスペースまたはサブスクリプションに対して「直近 1 時間のエラーを Log Analytics で確認して」などと問い合わせることで、代表的なエラー件数と概要を日本語で要約して返せるようにする。

**Independent Test**: 既知のエラーが記録されたテスト用 Log Analytics ワークスペースに対し、CLI から時間範囲指定付きで問い合わせたとき、エラー種別ごとの件数と代表メッセージが要約されることを pytest から自動検証できる。

### Tests for User Story 3 ⚠️

- [ ] T026 [P] [US3] Add agent tests for Log Analytics error summarization in tests/azure_mcp_agent/test_log_analytics.py
- [ ] T027 [P] [US3] Add CLI tests for error summary queries in tests/azure_mcp_agent/test_cli.py

### Implementation for User Story 3

- [ ] T028 [P] [US3] Implement MCP call for querying Log Analytics workspaces for error logs in src/azure_mcp_agent/mcp_client.py
- [ ] T029 [P] [US3] Implement agent intent handling for Log Analytics error summary queries in src/azure_mcp_agent/agent.py
- [ ] T030 [US3] Implement aggregation and bucketing logic for error counts and representative messages in src/azure_mcp_agent/agent.py
- [ ] T031 [US3] Implement Japanese error summary formatting (3〜5 ステップの簡潔なトラブルシュートガイド含む) in src/azure_mcp_agent/agent.py
- [ ] T032 [US3] Implement CLI interaction patterns for specifying time ranges and scopes in src/azure_mcp_agent/cli.py

**Checkpoint**: All three user stories should now be independently functional and covered by tests

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T033 [P] Add detailed usage and examples to specs/001-azure-resource-guide-agent/quickstart.md
- [ ] T034 Improve logging and error reporting across src/azure_mcp_agent/agent.py and src/azure_mcp_agent/cli.py
- [ ] T035 [P] Add additional edge-case tests for permission errors and timeouts in tests/azure_mcp_agent/test_agent_basic.py
- [ ] T036 [P] Add basic performance checks for typical queries in tests/azure_mcp_agent/test_log_analytics.py
- [ ] T037 Refine prompts and safety constraints in src/azure_mcp_agent/prompts.py based on early feedback
- [ ] T038 Run end-to-end validation using specs/001-azure-resource-guide-agent/quickstart.md and adjust docs as needed

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - can start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 completion - BLOCKS all user stories
- **Phase 3 (US1)**: Depends on Phase 2 completion - can be implemented and shipped as MVP independently
- **Phase 4 (US2)**: Depends on Phase 2 completion - may reuse US1 patterns but remains independently testable
- **Phase 5 (US3)**: Depends on Phase 2 completion - may reuse US1/US2 patterns but remains independently testable
- **Phase 6 (Polish)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: First delivery target (MVP). No dependency on US2/US3.
- **User Story 2 (P2)**: Can start after foundational work; does not require US1 at runtime but can reuse its patterns.
- **User Story 3 (P3)**: Can start after foundational work; logically independent but conceptually benefits from US1/US2 patterns.

### Parallel Opportunities

- Phase 1 and Phase 2 tasks marked [P] can be implemented in parallel by different contributors.
- After Phase 2, tests and implementation tasks for US1, US2, and US3 marked [P] can proceed in parallel as long as they touch different files or clearly separated sections.
- Within each user story, MCP client extensions (mcp_client.py), agent behavior (agent.py), and CLI wiring (cli.py) can often be worked on in parallel if interfaces are agreed up front.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001–T004)
2. Complete Phase 2: Foundational (T005–T011)
3. Implement and test Phase 3: User Story 1 (T012–T018)
4. Validate end-to-end via CLI and tests, using quickstart.md steps
5. Optionally release as initial CLI-only Azure Resource Guide Agent

### Incremental Delivery

1. MVP (US1) delivered and validated
2. Add US2: storage account listing (Phase 4), including tests
3. Add US3: Log Analytics error summarization (Phase 5), including tests
4. Apply Phase 6 polish tasks based on feedback and usage

### Parallel Team Strategy

- Developer A: Focus on MCP client and config (T005–T006, T014, T021, T028)
- Developer B: Focus on agent behavior and prompts (T007–T008, T015–T016, T022–T023, T029–T031)
- Developer C: Focus on CLI wiring and tests (T009–T010, T012–T013, T019–T020, T026–T027, T032–T038)

All tasks are designed to be specific and independently executable by an LLM or human developer with access to this repository.
