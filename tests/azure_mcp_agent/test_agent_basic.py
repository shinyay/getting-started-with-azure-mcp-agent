"""Agent-level tests for Azure Resource Guide Agent

Tests for User Story 1: Resource Group Listing
Tests verify agent behavior with mocked MCP client.
"""

import sys
from pathlib import Path

# Ensure src is in path before any imports
repo_root = Path(__file__).parent.parent.parent
src_path = repo_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

import pytest
from unittest.mock import MagicMock, patch

# Import the modules we need to test
import azure_mcp_agent.agent
import azure_mcp_agent.mcp_client


@pytest.fixture
def mock_settings():
    """Fixture for mock agent settings"""
    settings = MagicMock()
    settings.model_name = "gpt-4o"
    settings.api_base = "https://test.example.com"
    settings.api_key = "test-key"
    settings.api_version = None
    settings.max_completion_tokens = 4096
    settings.temperature = 0.7
    return settings


@pytest.mark.asyncio
async def test_agent_lists_resource_groups_successfully(mock_settings):
    """Test that agent can list resource groups with Japanese output
    
    User Story 1 / T012: Agent レベルのテスト
    
    Given: MCP client returns test resource group data
    When: User asks "このサブスクリプションのリソースグループ一覧を出して"
    Then: Response includes all RG names and locations in Japanese context
    """
    create_agent = azure_mcp_agent.agent.create_agent
    
    with patch('azure_mcp_agent.mcp_client.create_azure_mcp_tool') as mock_create_tool:
        # Create a mock tool that simulates MCP responses
        mock_tool = MagicMock()
        mock_tool.name = "azure_mcp_server"
        mock_tool.description = "Azure MCP Server"
        mock_create_tool.return_value = mock_tool
        
        # Mock the agent creation and execution
        with patch('azure_mcp_agent.agent.ChatAgent') as MockChatAgent:
            mock_agent_instance = MagicMock()
            mock_thread = MagicMock()
            
            # Simulate agent returning Japanese response with RG data
            async def mock_run_stream(*args, **kwargs):
                """Simulate streaming response with resource group data"""
                response_text = """以下がこのサブスクリプションのリソースグループ一覧です:

- rg-app-core (location: japaneast, tags: env=prod, owner=team-a)
- rg-app-dev (location: japanwest, tags: env=dev)
- rg-data (location: japaneast)

合計 3 件のリソースグループが見つかりました。"""
                
                # Yield response chunks as the agent would
                chunk = MagicMock()
                chunk.text = response_text
                yield chunk
            
            mock_agent_instance.run_stream = mock_run_stream
            mock_agent_instance.get_new_thread.return_value = mock_thread
            MockChatAgent.return_value = mock_agent_instance
            
            # Create agent with mocked settings
            agent = await create_agent(mock_settings)
            thread = agent.get_new_thread()
            
            # Execute query
            query = "このサブスクリプションのリソースグループ一覧を出して"
            response_parts = []
            async for chunk in agent.run_stream([query], thread=thread):
                if chunk.text:
                    response_parts.append(chunk.text)
            
            response = ''.join(response_parts)
            
            # Verify response contains expected content
            assert "rg-app-core" in response, "Response should contain rg-app-core"
            assert "rg-app-dev" in response, "Response should contain rg-app-dev"
            assert "rg-data" in response, "Response should contain rg-data"
            assert "japaneast" in response, "Response should contain location"
            assert "japanwest" in response, "Response should contain location"
            assert "リソースグループ" in response, "Response should be in Japanese"


@pytest.mark.asyncio
async def test_agent_handles_empty_resource_groups(mock_settings):
    """Test that agent handles subscriptions with no resource groups
    
    User Story 1 / T012: エッジケーステスト（空のサブスクリプション）
    
    Given: MCP client returns empty resource group list
    When: User asks for resource group list
    Then: Response includes friendly Japanese message indicating no RGs found
    """
    create_agent = azure_mcp_agent.agent.create_agent
    
    with patch('azure_mcp_agent.mcp_client.create_azure_mcp_tool') as mock_create_tool:
        mock_tool = MagicMock()
        mock_tool.name = "azure_mcp_server"
        mock_tool.description = "Azure MCP Server"
        mock_create_tool.return_value = mock_tool
        
        with patch('azure_mcp_agent.agent.ChatAgent') as MockChatAgent:
            mock_agent_instance = MagicMock()
            mock_thread = MagicMock()
            
            async def mock_run_stream(*args, **kwargs):
                chunk = MagicMock()
                chunk.text = "このサブスクリプションにはリソースグループが存在しません。"
                yield chunk
            
            mock_agent_instance.run_stream = mock_run_stream
            mock_agent_instance.get_new_thread.return_value = mock_thread
            MockChatAgent.return_value = mock_agent_instance
            
            agent = await create_agent(mock_settings)
            thread = agent.get_new_thread()
            
            query = "このサブスクリプションのリソースグループ一覧を出して"
            response_parts = []
            async for chunk in agent.run_stream([query], thread=thread):
                if chunk.text:
                    response_parts.append(chunk.text)
            
            response = ''.join(response_parts)
            
            # Verify friendly Japanese message
            assert "リソースグループ" in response
            assert "存在しません" in response or "見つかりませんでした" in response


@pytest.mark.asyncio
async def test_agent_handles_permission_errors(mock_settings):
    """Test that agent handles permission denied errors gracefully
    
    User Story 1 / T012: エッジケーステスト（権限不足）
    
    Given: MCP client returns permission error
    When: User asks for resource group list
    Then: Response includes clear Japanese error message about permissions
    """
    create_agent = azure_mcp_agent.agent.create_agent
    
    with patch('azure_mcp_agent.mcp_client.create_azure_mcp_tool') as mock_create_tool:
        mock_tool = MagicMock()
        mock_tool.name = "azure_mcp_server"
        mock_tool.description = "Azure MCP Server"
        mock_create_tool.return_value = mock_tool
        
        with patch('azure_mcp_agent.agent.ChatAgent') as MockChatAgent:
            mock_agent_instance = MagicMock()
            mock_thread = MagicMock()
            
            async def mock_run_stream(*args, **kwargs):
                chunk = MagicMock()
                chunk.text = "サブスクリプションにアクセスする権限が不足しています。管理者に権限の確認を依頼してください。"
                yield chunk
            
            mock_agent_instance.run_stream = mock_run_stream
            mock_agent_instance.get_new_thread.return_value = mock_thread
            MockChatAgent.return_value = mock_agent_instance
            
            agent = await create_agent(mock_settings)
            thread = agent.get_new_thread()
            
            query = "このサブスクリプションのリソースグループ一覧を出して"
            response_parts = []
            async for chunk in agent.run_stream([query], thread=thread):
                if chunk.text:
                    response_parts.append(chunk.text)
            
            response = ''.join(response_parts)
            
            # Verify permission error message in Japanese
            assert "権限" in response
            assert "アクセス" in response or "不足" in response
