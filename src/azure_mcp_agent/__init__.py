"""Azure Resource Guide Agent - Azure MCP Server を経由して Azure リソースを日本語で調査できる CLI エージェント"""

__version__ = "0.1.0"

from .agent import create_agent, create_agent_sync
from .config import get_settings, Settings
from .prompts import get_system_prompt

__all__ = [
    "__version__",
    "create_agent",
    "create_agent_sync",
    "get_settings",
    "Settings",
    "get_system_prompt",
]
