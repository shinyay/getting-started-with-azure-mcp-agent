"""Pytest configuration for azure_mcp_agent tests"""

import sys
from pathlib import Path

# Ensure src is at the beginning of sys.path to avoid importing from tests/azure_mcp_agent
repo_root = Path(__file__).parent.parent
src_path = repo_root / "src"

# Remove any tests paths that might interfere
paths_to_remove = [
    p for p in sys.path
    if p.endswith("tests/azure_mcp_agent") or (len(Path(p).parts) >= 2 and tuple(Path(p).parts[-2:]) == ("tests", "azure_mcp_agent"))
]
for p in paths_to_remove:
    sys.path.remove(p)

# Insert src at the beginning
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


# ============================================================================
# Shared Test Response Templates
# ============================================================================

# These templates ensure consistency with prompts.py and avoid duplication

MOCK_STORAGE_ACCOUNTS_RESPONSE = """リソースグループ「{rg_name}」内のストレージアカウント一覧:

- stappcore001 (location: japaneast, kind: StorageV2, sku: Standard_LRS)
- stappcore002 (location: japaneast, kind: BlobStorage, sku: Standard_GRS)
- stappcorelogs (location: japanwest, kind: StorageV2, sku: Standard_ZRS)

合計 3 件のストレージアカウントが見つかりました。"""

MOCK_EMPTY_STORAGE_ACCOUNTS_RESPONSE = "リソースグループ「{rg_name}」にはストレージアカウントが見つかりませんでした。"

MOCK_RESOURCE_GROUP_NOT_FOUND_RESPONSE = "指定されたリソースグループ「{rg_name}」が見つかりませんでした。リソースグループ名を確認してください。"


# ============================================================================
# Log Analytics Error Summarization Templates (User Story 3)
# ============================================================================

MOCK_LOG_ANALYTICS_ERROR_SUMMARY = """直近 {timespan} のエラー状況を要約しました。

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
4. 高 CPU 使用率の警告については、アプリケーションのスケールアウトやコード最適化を検討してください。"""

MOCK_NO_ERRORS_FOUND_RESPONSE = "指定期間にエラーは検出されませんでした。"

MOCK_LOG_ANALYTICS_PERMISSION_ERROR = "Log Analytics ワークスペースにアクセスする権限が不足しています。Azure の権限設定を確認してください。"

MOCK_LOG_ANALYTICS_TIMEOUT_ERROR = "Azure 側で一時的な問題が発生しています。時間をおいて再実行してください。"
