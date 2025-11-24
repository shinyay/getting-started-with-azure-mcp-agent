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

### User Story 1: リソースグループ一覧

**質問例:**
```
このサブスクリプションのリソースグループ一覧を出して
```

**期待される応答例:**
```
エージェント: 以下がこのサブスクリプションのリソースグループ一覧です:

- rg-app-core (location: japaneast, tags: env=prod, owner=team-a)
- rg-app-dev (location: japanwest, tags: env=dev)
- rg-data (location: japaneast, tags: project=analytics)
- rg-network (location: japaneast, tags: env=prod)

合計 4 件のリソースグループが見つかりました。
```

**エラー例（権限不足の場合）:**
```
エージェント: サブスクリプションにアクセスする権限が不足しています。管理者に権限の確認を依頼してください。
```

---

### User Story 2: ストレージアカウント一覧

**質問例:**
```
rg-app-core のストレージアカウントを一覧して
```

**期待される応答例:**
```
エージェント: リソースグループ「rg-app-core」内のストレージアカウント一覧:

- stappcore001 (location: japaneast, kind: StorageV2, sku: Standard_LRS)
- stappcore002 (location: japaneast, kind: BlobStorage, sku: Standard_GRS)
- stappcorelogs (location: japanwest, kind: StorageV2, sku: Standard_ZRS)

合計 3 件のストレージアカウントが見つかりました。
```

**エラー例（リソースグループが存在しない場合）:**
```
エージェント: 指定されたリソースグループ「rg-not-exist」が見つかりませんでした。リソースグループ名を確認してください。
```

**空のリソースグループの場合:**
```
エージェント: リソースグループ「rg-empty」にはストレージアカウントが見つかりませんでした。
```

---

### User Story 3: Log Analytics エラー要約

**質問例1: ワークスペースを指定せずに確認**
```
直近1時間のエラーをLog Analyticsで確認して
```

**質問例2: ワークスペースを指定して確認**
```
workspace-app-prod の直近24時間のエラーを確認して
```

**期待される応答例:**
```
エージェント: 直近 1 時間 のエラー状況を要約しました。

■ エラー件数の概要
- Application エラー: 12 件
- Platform エラー: 3 件
- Warning: 5 件

■ 代表的なエラーメッセージ
- Application: "Database connection timeout occurred" (resource: /subscriptions/sub-123/resourceGroups/rg-app/providers/Microsoft.Web/sites/app-web)
- Platform: "VM failed to start due to allocation error" (resource: /subscriptions/sub-123/resourceGroups/rg-infra/providers/Microsoft.Compute/virtualMachines/vm-01)
- Warning: "High CPU usage detected" (resource: /subscriptions/sub-123/resourceGroups/rg-app/providers/Microsoft.Web/sites/app-api)

■ 次に実行をおすすめする 3〜5 ステップ
1. Application エラーについて、該当リソースのメトリック（CPU/メモリ/接続数）を確認してください。
2. Database の接続文字列やネットワーク設定（NSG/Firewall）に変更がなかったかを確認してください。
3. Platform エラーが継続する場合は、別リージョンでのリソース再作成を検討してください。
4. 高 CPU 使用率の警告については、アプリケーションのスケールアウトやコード最適化を検討してください。
```

**エラー0件の場合:**
```
エージェント: 指定期間にエラーは検出されませんでした。
```

**複数ワークスペースがある場合:**
```
エージェント: 複数の Log Analytics ワークスペースが見つかりました。対象とするワークスペースを指定してください:

- workspace-app-prod (location: japaneast)
- workspace-infra-prod (location: japanwest)
- workspace-dev (location: japaneast)

例: "workspace-app-prod の直近1時間のエラーを確認して"
```

---

### その他の質問例

**時間範囲の指定:**
- `直近 1 時間のエラーを確認して`
- `過去 24 時間のエラーを教えて`
- `今日のエラー状況を見せて`

### 終了方法

- `exit` または `quit` と入力
- Ctrl+C を押す
- Ctrl+D を押す

## 現在の実装状況（Phase 6 完了時点）

✅ **実装済み:**

### 基盤機能（Phase 1-2）
- 設定管理（config.py）
- Azure MCP クライアント接続（mcp_client.py）
- 日本語プロンプト・システムインストラクション（prompts.py）
- エージェント本体（agent.py）
- 対話型 CLI（cli.py）
- メインエントリポイント（main.py）
- **ロギング機能** - Python logging を使用した診断ログ（Phase 6）
  - 環境変数 `AZURE_MCP_AGENT_LOG_LEVEL` でログレベル制御可能
  - デフォルト: INFO レベル、標準エラー出力（stderr）に出力
- **エラーハンドリング** - ユーザーフレンドリーな日本語エラーメッセージ（Phase 6）
  - スタックトレースを非表示
  - 権限エラー・タイムアウト・一時障害の適切な処理

### User Story 1: リソースグループ一覧（Phase 3）
- 日本語での自然言語クエリに対応
- 空のサブスクリプション・権限エラーのハンドリング
- テストコード完備（test_agent_basic.py, test_cli.py）
- エッジケーステスト: 権限不足、タイムアウト、一時障害（Phase 6）

### User Story 2: ストレージアカウント一覧（Phase 4）
- 特定リソースグループ内のストレージアカウント情報取得
- 名前・リージョン・種別・SKU 名を原文表記で表示
- 存在しないリソースグループ・空のリソースグループのハンドリング
- テストコード完備（test_agent_basic.py, test_cli.py）
- エッジケーステスト: 権限不足、存在しないリソースグループ（Phase 6）

### User Story 3: Log Analytics エラー要約（Phase 5）
- Log Analytics を用いたエラー状況の把握
- エラー件数の集計（severity / category 別）
- 代表的なエラーメッセージの抽出
- 3〜5 ステップの簡潔なトラブルシュートガイド（FR-008）
- 期間指定（直近1時間、24時間など）の自然言語サポート
- ワークスペース選択・権限エラー・エラー0件などのエッジケース対応
- テストコード完備（test_log_analytics.py, test_cli.py）
- パフォーマンステスト: 大量エラー（500件）の要約処理（Phase 6）

### Phase 6: Polish & Cross-Cutting Concerns ✨
- **ロギング強化**: MCP ツール呼び出しと重要なエラーの詳細ログ
- **プロンプト改善**: 読み取り専用・日本語応答・あいまい入力処理の明文化
- **エッジケーステスト**: タイムアウト、一時障害、権限エラーの網羅的テスト
- **パフォーマンステスト**: 大量データ（100 RG、50 SA、500 errors）の処理検証
- **ドキュメント充実**: 詳細な使用例と期待される応答の追加

**テスト状況:**
- 合計 42 テスト（Phase 1-6）
- すべてのテストが成功

## トラブルシューティング

### 環境変数が設定されていないエラー

```
設定エラー: 必須の環境変数が設定されていません
```

**原因:** LLM API への接続に必要な環境変数が設定されていません。

**解決方法:**
1. GitHub Models を使用する場合:
   ```bash
   export GITHUB_MODEL_NAME="gpt-4o"
   export GITHUB_API_KEY="your-github-token-here"
   export GITHUB_API_BASE="https://models.inference.ai.azure.com"
   ```

2. Azure OpenAI を使用する場合:
   ```bash
   export AZURE_OPENAI_MODEL_NAME="your-deployment-name"
   export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
   export AZURE_OPENAI_API_KEY="your-api-key-here"
   ```

---

### MCP Server への接続エラー

```
接続エラー: Azure MCP Server への接続に失敗しました
```

**原因:** Azure MCP Server との通信に問題があります。

**解決方法:**
1. Node.js / npm がインストールされているか確認:
   ```bash
   node --version
   npm --version
   ```

2. Azure 認証が完了しているか確認:
   ```bash
   az login
   az account show
   ```

3. Azure MCP Server を手動で起動して動作確認:
   ```bash
   npx -y @azure/mcp@latest server start --read-only
   ```

---

### Node.js が見つからないエラー

```
警告: MCP サーバーコマンド 'npx' が見つかりません。
```

**原因:** Node.js がインストールされていないか、PATH が通っていません。

**解決方法:**
- **macOS**: `brew install node`
- **Ubuntu/Debian**: `sudo apt install nodejs npm`
- **Windows**: https://nodejs.org/ からインストーラーをダウンロード
- **その他**: https://nodejs.org/

インストール後、以下で確認:
```bash
node --version
npm --version
```

---

### 権限エラー（Permission Denied）

```
サブスクリプションにアクセスする権限が不足しています
```

**原因:** Azure サブスクリプションやリソースへのアクセス権限がありません。

**解決方法:**
1. Azure ポータルで、適切な RBAC ロールが割り当てられているか確認
   - 最小権限: `Reader` ロール（読み取り専用）
   - Log Analytics: `Log Analytics Reader` ロール
   
2. 正しいサブスクリプションにログインしているか確認:
   ```bash
   az account show
   az account list --output table
   az account set --subscription <subscription-id>
   ```

---

### タイムアウトエラー

```
リクエストがタイムアウトしました。時間をおいて再度実行してください。
```

**原因:** Azure API の応答が遅い、またはネットワークに問題があります。

**解決方法:**
1. しばらく時間をおいて再実行
2. ネットワーク接続を確認
3. Azure のサービス正常性ステータスを確認: https://status.azure.com/

---

### ログの有効化

詳細なログを確認したい場合は、以下の環境変数を設定してください:

```bash
export AZURE_MCP_AGENT_LOG_LEVEL=DEBUG
```

ログレベルの選択肢:
- `DEBUG`: 最も詳細（開発・デバッグ用）
- `INFO`: 通常の情報（デフォルト）
- `WARNING`: 警告のみ
- `ERROR`: エラーのみ

**⚠️ セキュリティに関する注意:**
- `DEBUG` レベルでは、問い合わせ内容の最初の100文字がログに記録されます
- 問い合わせに機密情報（接続文字列、パスワード、アクセストークンなど）を含めないでください
- 本番環境では `INFO` 以上のログレベルを使用することを推奨します

## 期待される動作

このエージェントは以下の動作を保証します:

### セキュリティ
- **完全読み取り専用**: Azure リソースの作成・更新・削除は一切行いません
- **秘密情報の保護**: トークンや接続文字列などの秘密情報は表示しません
- **最小権限の原則**: Azure Reader ロールのみで動作します

### 応答品質
- **日本語応答**: すべての説明とエラーメッセージは日本語で表示
- **原文保持**: Azure リソース名、ID、SKU、リージョン名は英数字のまま表示
- **最新情報**: MCP を通じて常に最新の Azure 状態を取得

### エラーハンドリング
- **ユーザーフレンドリー**: スタックトレースは表示せず、分かりやすい日本語メッセージを表示
- **詳細ログ**: 問題診断のため、内部では詳細なログを記録（stderr に出力）
- **エッジケース対応**: 権限不足、タイムアウト、一時障害などを適切に処理

## 次のステップ

このクイックスタートを完了したら、以下のドキュメントも参照してください:

- **プロダクト仕様**: `specs/001-azure-resource-guide-agent/spec.md` - 機能要件の詳細
- **実装プラン**: `specs/001-azure-resource-guide-agent/plan.md` - アーキテクチャと設計判断
- **データモデル**: `specs/001-azure-resource-guide-agent/data-model.md` - データ構造の定義

### フィードバックと貢献

問題を発見した場合や機能要望がある場合は、GitHub Issues でお知らせください:
https://github.com/shinyay/getting-started-with-azure-mcp-agent/issues
