"""Pytest configuration for azure_mcp_agent tests"""

import sys
from pathlib import Path

# Ensure src is at the beginning of sys.path to avoid importing from tests/azure_mcp_agent
repo_root = Path(__file__).parent.parent
src_path = repo_root / "src"

# Remove any tests paths that might interfere
paths_to_remove = [
    p for p in sys.path
    if p.endswith("tests/azure_mcp_agent") or tuple(Path(p).parts[-2:]) == ("tests", "azure_mcp_agent")
]
for p in paths_to_remove:
    sys.path.remove(p)

# Insert src at the beginning
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
