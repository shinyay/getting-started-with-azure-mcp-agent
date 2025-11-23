"""Main entrypoint wrapper for Azure Resource Guide Agent

This module provides a simple entrypoint that delegates to cli.main().
Can be run directly with: python src/azure_mcp_agent/main.py
"""

import sys
from pathlib import Path

# Add src to path when running directly
if __name__ == "__main__":
    src_path = Path(__file__).parent.parent
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    from azure_mcp_agent.cli import main
    sys.exit(main())
