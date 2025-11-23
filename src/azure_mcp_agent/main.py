"""Main entrypoint wrapper for Azure Resource Guide Agent

This module provides a simple entrypoint that delegates to cli.main().
Can be run directly with: python src/azure_mcp_agent/main.py
"""

import sys
from .cli import main

if __name__ == "__main__":
    sys.exit(main())
