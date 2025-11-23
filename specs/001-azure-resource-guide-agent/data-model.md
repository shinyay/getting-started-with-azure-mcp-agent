# Data Model: Azure Resource Guide Agent

**Feature**: ../spec.md
**Date**: 2025-11-23

## Entities

### サブスクリプション
- **Description**: Azure リソースの論理的なコンテナ。
- **Fields** (logical, not implementation-specific):
  - `subscription_id`: 一意な識別子 (string)
  - `display_name`: 表示名 (string)
  - `tenant_id`: 関連するテナント ID (string)
- **Relationships**:
  - 1 対多で複数のリソースグループを保持する。

### リソースグループ
- **Description**: サブスクリプション内のリソースをまとめる論理グループ。
- **Fields**:
  - `name`: リソースグループ名 (string)
  - `location`: リージョン (string)
  - `tags`: タグのキー・バリュー (map<string, string>)
  - `subscription_id`: 所属サブスクリプション ID (string)
- **Relationships**:
  - 1 対多で複数のリソース（ストレージアカウントなど）を保持する。

### ストレージアカウント
- **Description**: ストレージサービスを提供するリソース。
- **Fields**:
  - `name`: アカウント名 (string)
  - `resource_group`: 所属リソースグループ名 (string)
  - `location`: リージョン (string)
  - `kind`: 種別 (string)
  - `sku_name`: SKU 名 (string)
- **Relationships**:
  - 特定のリソースグループに所属する。

### Log Analytics ワークスペース
- **Description**: ログやメトリックを集約するワークスペース。
- **Fields**:
  - `name`: ワークスペース名 (string)
  - `resource_group`: 所属リソースグループ名 (string)
  - `location`: リージョン (string)
  - `workspace_id`: ワークスペース識別子 (string)
- **Relationships**:
  - 複数のエラーイベントを保持しうる。

### エラーイベント
- **Description**: Log Analytics に記録されるエラーの論理的単位。
- **Fields**:
  - `timestamp`: 発生時刻 (datetime)
  - `severity`: 重大度レベル (string)
  - `category`: カテゴリ / ソース (string)
  - `message`: メッセージ概要 (string)
  - `resource_id`: 関連リソース ID (string)
- **Relationships**:
  - 特定の Log Analytics ワークスペースに紐づく。

## Derived Views

### リソースグループ一覧ビュー
- **Inputs**:
  - `subscription_id`
- **Outputs**:
  - リソースグループごとの `name`, `location`, `tags` の一覧

### ストレージアカウント一覧ビュー
- **Inputs**:
  - `subscription_id`
  - `resource_group`
- **Outputs**:
  - ストレージアカウントごとの `name`, `location`, `kind`, `sku_name` の一覧

### エラー要約ビュー
- **Inputs**:
  - 対象となる `workspace_id` または `subscription_id`
  - 期間（例: 過去 1 時間）
- **Outputs**:
  - エラー種別ごとの件数
  - 代表的な `message` のサンプル
  - 必要に応じたシンプルな日本語サマリテキスト
