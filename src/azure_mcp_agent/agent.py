"""Core Agent implementation for Azure Resource Guide Agent

This module provides the ChatAgent implementation using Microsoft Agent Framework.
The agent connects to Azure MCP Server for read-only Azure resource queries.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Optional

from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient
from openai import AsyncOpenAI

from .config import Settings, get_settings
from .mcp_client import create_azure_mcp_tool
from .prompts import get_system_prompt

# Configure logger for this module
logger = logging.getLogger(__name__)


async def create_agent(settings: Optional[Settings] = None) -> ChatAgent:
    """Create a configured ChatAgent for Azure resource queries
    
    Args:
        settings: Optional settings object. If not provided, loads from environment.
        
    Returns:
        ChatAgent: Configured agent ready for queries
        
    Raises:
        ValueError: If required configuration is missing
        RuntimeError: If MCP connection cannot be established
    """
    if settings is None:
        settings = get_settings()
    
    logger.info("エージェントの初期化を開始しています")
    logger.debug(f"使用モデル: {settings.model_name}, API Base: {settings.api_base}")
    
    try:
        # Create OpenAI-compatible client for GitHub Models or Azure OpenAI
        openai_client = AsyncOpenAI(
            base_url=settings.api_base,
            api_key=settings.api_key,
            default_query={"api-version": settings.api_version} if settings.api_version else None,
        )
        
        # Create chat client
        chat_client = OpenAIChatClient(
            async_client=openai_client,
            model_id=settings.model_name,
        )
        logger.debug("OpenAI チャットクライアントを作成しました")
        
        # Create MCP tool for Azure resource access
        logger.info("Azure MCP ツールを作成しています")
        mcp_tool = create_azure_mcp_tool(settings)
        logger.info("Azure MCP ツールの作成が完了しました")
        
        # Create agent with system prompt and tools
        agent = ChatAgent(
            chat_client=chat_client,
            instructions=get_system_prompt(),
            max_completion_tokens=settings.max_completion_tokens,
            temperature=settings.temperature,
            tools=[mcp_tool],
        )
        
        logger.info("エージェントの初期化が完了しました")
        return agent
        
    except ValueError as e:
        logger.error(f"設定エラー: {e}")
        raise
    except RuntimeError as e:
        logger.error(f"MCP 接続エラー: {e}")
        raise
    except Exception as e:
        logger.error(f"エージェント初期化中の予期しないエラー: {e}", exc_info=True)
        raise RuntimeError(f"エージェントの初期化に失敗しました: {e}") from e


def create_agent_sync(settings: Optional[Settings] = None) -> ChatAgent:
    """Synchronous wrapper for create_agent
    
    Args:
        settings: Optional settings object. If not provided, loads from environment.
        
    Returns:
        ChatAgent: Configured agent ready for queries
    """
    return asyncio.run(create_agent(settings))
