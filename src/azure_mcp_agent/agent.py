"""Core Agent implementation for Azure Resource Guide Agent

This module provides the ChatAgent implementation using Microsoft Agent Framework.
The agent connects to Azure MCP Server for read-only Azure resource queries.
"""

import asyncio
from typing import Optional

from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient
from openai import AsyncOpenAI

from .config import Settings, get_settings
from .mcp_client import create_azure_mcp_tool
from .prompts import get_system_prompt


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
    
    # Create OpenAI-compatible client for GitHub Models or Azure OpenAI
    openai_client = AsyncOpenAI(
        base_url=settings.api_base,
        api_key=settings.api_key,
    )
    
    # Create chat client
    chat_client = OpenAIChatClient(
        async_client=openai_client,
        model=settings.model_name,
    )
    
    # Create MCP tool for Azure resource access
    mcp_tool = create_azure_mcp_tool(settings)
    
    # Create agent with system prompt and tools
    agent = ChatAgent(
        chat_client=chat_client,
        instructions=get_system_prompt(),
        max_completion_tokens=settings.max_completion_tokens,
        temperature=settings.temperature,
        tools=[mcp_tool],
    )
    
    return agent


def create_agent_sync(settings: Optional[Settings] = None) -> ChatAgent:
    """Synchronous wrapper for create_agent
    
    Args:
        settings: Optional settings object. If not provided, loads from environment.
        
    Returns:
        ChatAgent: Configured agent ready for queries
    """
    return asyncio.run(create_agent(settings))
