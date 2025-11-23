"""Azure MCP Server client wrapper

This module provides a wrapper around Microsoft Agent Framework's MCPStdioTool
to connect to Azure MCP Server for read-only Azure resource queries.
"""

from agent_framework import MCPStdioTool
from .config import Settings
from .prompts import TOOL_DESCRIPTIONS, get_error_message


def create_azure_mcp_tool(settings: Settings) -> MCPStdioTool:
    """Create an MCPStdioTool configured for Azure MCP Server
    
    Args:
        settings: Configuration settings containing MCP connection details
        
    Returns:
        MCPStdioTool: Configured MCP tool for Azure resource access
        
    Raises:
        RuntimeError: If MCP server connection cannot be established
    """
    try:
        tool = MCPStdioTool(
            name="azure_mcp_server",
            description=TOOL_DESCRIPTIONS["azure_mcp"],
            command=settings.mcp_command,
            args=settings.mcp_args,
        )
        return tool
    except Exception as e:
        error_msg = get_error_message("mcp_connection_error")
        args_str = ' '.join(settings.mcp_args) if settings.mcp_args else ''
        raise RuntimeError(
            f"{error_msg}\n\n"
            f"詳細情報:\n"
            f"  - コマンド: {settings.mcp_command} {args_str}\n"
            f"  - エラー: {e}\n"
        ) from e


def validate_mcp_connection(tool: MCPStdioTool) -> bool:
    """Validate that the MCP tool can connect to Azure MCP Server
    
    This is a simple check to ensure the tool is properly configured.
    Actual connection validation happens when the tool is first used by the agent.
    
    Args:
        tool: The MCP tool to validate
        
    Returns:
        bool: True if tool appears to be properly configured
    """
    # Basic validation - check that tool has required attributes
    return (
        hasattr(tool, 'name') and 
        hasattr(tool, 'description') and
        tool.name == "azure_mcp_server"
    )
