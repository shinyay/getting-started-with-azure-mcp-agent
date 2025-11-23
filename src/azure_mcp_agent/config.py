"""Configuration loader for Azure Resource Guide Agent

This module manages configuration for:
- LLM model settings (GitHub Models or Azure OpenAI)
- Azure MCP Server connection settings
- Agent behavior settings
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Settings:
    """Configuration settings for Azure Resource Guide Agent"""
    
    # LLM Model Settings (GitHub Models or Azure OpenAI)
    model_name: str
    api_base: str
    api_key: str
    api_version: Optional[str] = None
    
    # Azure MCP Server Settings
    mcp_command: str = "npx"
    mcp_args: list[str] = field(default_factory=lambda: [
        "-y",
        "@azure/mcp@latest",
        "server",
        "start",
        "--read-only"
    ])
    
    # Agent Settings
    max_completion_tokens: int = 4096
    temperature: float = 0.7


def get_settings() -> Settings:
    """Load settings from environment variables
    
    Returns:
        Settings: Configuration settings object
        
    Raises:
        ValueError: If required environment variables are missing
    """
    # Required environment variables
    model_name = os.getenv("GITHUB_MODEL_NAME") or os.getenv("AZURE_OPENAI_MODEL_NAME")
    api_base = os.getenv("GITHUB_API_BASE") or os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("GITHUB_API_KEY") or os.getenv("AZURE_OPENAI_API_KEY")
    
    # Validate required settings
    missing_vars = []
    if not model_name:
        missing_vars.append("GITHUB_MODEL_NAME or AZURE_OPENAI_MODEL_NAME")
    if not api_base:
        missing_vars.append("GITHUB_API_BASE or AZURE_OPENAI_ENDPOINT")
    if not api_key:
        missing_vars.append("GITHUB_API_KEY or AZURE_OPENAI_API_KEY")
    
    if missing_vars:
        raise ValueError(
            f"必須の環境変数が設定されていません: {', '.join(missing_vars)}\n\n"
            "以下の環境変数を設定してください:\n"
            "  GitHub Models を使用する場合:\n"
            "    - GITHUB_MODEL_NAME: モデル名 (例: gpt-4o)\n"
            "    - GITHUB_API_BASE: APIエンドポイント (例: https://models.inference.ai.azure.com)\n"
            "    - GITHUB_API_KEY: GitHub Personal Access Token\n\n"
            "  Azure OpenAI を使用する場合:\n"
            "    - AZURE_OPENAI_MODEL_NAME: デプロイメント名\n"
            "    - AZURE_OPENAI_ENDPOINT: Azure OpenAI エンドポイント\n"
            "    - AZURE_OPENAI_API_KEY: Azure OpenAI API キー\n\n"
            "詳細は quickstart.md を参照してください。"
        )
    
    # Optional settings
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    
    # MCP Server settings (with defaults)
    mcp_command = os.getenv("AZURE_MCP_COMMAND", "npx")
    mcp_args_str = os.getenv("AZURE_MCP_ARGS")
    mcp_args = mcp_args_str.split(",") if mcp_args_str else None
    
    # Agent settings
    max_tokens = int(os.getenv("MAX_COMPLETION_TOKENS", "4096"))
    temperature = float(os.getenv("TEMPERATURE", "0.7"))
    
    # Build settings kwargs, only include mcp_args if explicitly set
    settings_kwargs = dict(
        model_name=model_name,
        api_base=api_base,
        api_key=api_key,
        api_version=api_version,
        mcp_command=mcp_command,
        max_completion_tokens=max_tokens,
        temperature=temperature,
    )
    if mcp_args is not None:
        settings_kwargs["mcp_args"] = mcp_args
    
    return Settings(**settings_kwargs)


def validate_mcp_server_available(settings: Optional[Settings] = None) -> bool:
    """Check if Azure MCP Server command is available
    
    Args:
        settings: Pre-loaded settings object. If None, settings will be loaded from environment.
    
    Returns:
        bool: True if MCP server command is available
    """
    import shutil
    if settings is None:
        settings = get_settings()
    return shutil.which(settings.mcp_command) is not None
