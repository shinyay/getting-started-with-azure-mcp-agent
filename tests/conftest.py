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
