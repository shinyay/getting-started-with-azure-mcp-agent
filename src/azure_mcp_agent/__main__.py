"""Allow running the CLI via python -m azure_mcp_agent"""

from azure_mcp_agent.cli import main

if __name__ == "__main__":
    import sys
    sys.exit(main())
