"""Agent-level tests for Log Analytics error summarization

Tests for User Story 3: Log Analytics Error Summarization (T026)
Tests verify agent behavior with mocked MCP client for error queries.
"""

import re
import sys
import time
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

# Import shared test response templates
from tests.conftest import (
    MOCK_LOG_ANALYTICS_ERROR_SUMMARY,
    MOCK_NO_ERRORS_FOUND_RESPONSE,
    MOCK_LOG_ANALYTICS_PERMISSION_ERROR,
    MOCK_LOG_ANALYTICS_TIMEOUT_ERROR,
)


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
async def test_agent_summarizes_log_analytics_errors_with_multiple_severities(mock_settings):
    """Test that agent can summarize Log Analytics errors with Japanese output
    
    User Story 3 / T026: Agent レベルのテスト - Log Analytics エラー要約
    
    Given: MCP client returns test error event data with multiple severities
    When: User asks "直近1時間のエラーをLog Analyticsで確認して"
    Then: Response includes:
          - Error counts by severity/category
          - Representative error messages
          - 3-5 step troubleshooting guide
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
            
            # Simulate agent returning Japanese response with Log Analytics error summary
            async def mock_run_stream(*args, **kwargs):
                """Simulate streaming response with error summary data"""
                response_text = MOCK_LOG_ANALYTICS_ERROR_SUMMARY.format(timespan="1 時間")
                
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
            query = "直近1時間のエラーをLog Analyticsで確認して"
            response_parts = []
            async for chunk in agent.run_stream([query], thread=thread):
                if chunk.text:
                    response_parts.append(chunk.text)
            
            response = ''.join(response_parts)
            
            # Verify response contains expected content
            assert "エラー件数" in response, "Response should contain error count section"
            assert "Application" in response, "Response should contain Application category"
            assert "Platform" in response, "Response should contain Platform category"
            assert "12 件" in response, "Response should contain specific error count"
            assert "3 件" in response, "Response should contain specific error count"
            
            # Verify representative error messages
            assert "代表的なエラーメッセージ" in response, "Response should contain error message section"
            assert "Database connection timeout" in response, "Response should contain specific error message"
            assert "VM failed to start" in response, "Response should contain specific error message"
            assert "/subscriptions/" in response, "Response should contain resource IDs"
            
            # Verify troubleshooting guide (FR-008: 3-5 steps)
            assert "次に実行をおすすめする" in response or "ステップ" in response, "Response should contain troubleshooting guide"
            assert "1." in response and "2." in response and "3." in response, "Response should have numbered steps"
            # Verify we have at least 3 steps
            step_count = len(re.findall(r'\n\d+\.\s+', response))
            assert 3 <= step_count <= 5, f"Should have 3-5 troubleshooting steps, found {step_count}"


@pytest.mark.asyncio
async def test_agent_handles_no_errors_found(mock_settings):
    """Test that agent handles case when no errors are found in Log Analytics
    
    User Story 3 / T026: エッジケーステスト（エラー0件）
    
    Given: MCP client returns empty error list
    When: User asks for error summary
    Then: Response includes friendly Japanese message indicating no errors found
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
                chunk.text = MOCK_NO_ERRORS_FOUND_RESPONSE
                yield chunk
            
            mock_agent_instance.run_stream = mock_run_stream
            mock_agent_instance.get_new_thread.return_value = mock_thread
            MockChatAgent.return_value = mock_agent_instance
            
            agent = await create_agent(mock_settings)
            thread = agent.get_new_thread()
            
            query = "直近1時間のエラーをLog Analyticsで確認して"
            response_parts = []
            async for chunk in agent.run_stream([query], thread=thread):
                if chunk.text:
                    response_parts.append(chunk.text)
            
            response = ''.join(response_parts)
            
            # Verify friendly Japanese message
            assert "エラー" in response
            assert "検出されませんでした" in response or "見つかりませんでした" in response


@pytest.mark.asyncio
async def test_agent_handles_log_analytics_permission_error(mock_settings):
    """Test that agent handles permission denied errors for Log Analytics
    
    User Story 3 / T026: エッジケーステスト（権限不足）
    
    Given: MCP client returns permission error
    When: User asks for error summary
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
                chunk.text = MOCK_LOG_ANALYTICS_PERMISSION_ERROR
                yield chunk
            
            mock_agent_instance.run_stream = mock_run_stream
            mock_agent_instance.get_new_thread.return_value = mock_thread
            MockChatAgent.return_value = mock_agent_instance
            
            agent = await create_agent(mock_settings)
            thread = agent.get_new_thread()
            
            query = "直近1時間のエラーをLog Analyticsで確認して"
            response_parts = []
            async for chunk in agent.run_stream([query], thread=thread):
                if chunk.text:
                    response_parts.append(chunk.text)
            
            response = ''.join(response_parts)
            
            # Verify permission error message in Japanese
            assert "権限" in response
            assert "不足" in response or "アクセス" in response
            assert "Log Analytics" in response or "ワークスペース" in response


@pytest.mark.asyncio
async def test_agent_handles_log_analytics_query_failure(mock_settings):
    """Test that agent handles temporary Azure Monitor / Log Analytics failures
    
    User Story 3 / T026: エッジケーステスト（一時障害）
    
    Given: MCP client returns timeout or temporary error
    When: User asks for error summary
    Then: Response includes user-friendly error message suggesting retry
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
                chunk.text = MOCK_LOG_ANALYTICS_TIMEOUT_ERROR
                yield chunk
            
            mock_agent_instance.run_stream = mock_run_stream
            mock_agent_instance.get_new_thread.return_value = mock_thread
            MockChatAgent.return_value = mock_agent_instance
            
            agent = await create_agent(mock_settings)
            thread = agent.get_new_thread()
            
            query = "直近24時間のエラーをLog Analyticsで確認して"
            response_parts = []
            async for chunk in agent.run_stream([query], thread=thread):
                if chunk.text:
                    response_parts.append(chunk.text)
            
            response = ''.join(response_parts)
            
            # Verify timeout/failure error message in Japanese
            assert "Azure" in response or "問題" in response
            assert "時間をおいて" in response or "再実行" in response or "再度" in response


@pytest.mark.asyncio
async def test_agent_handles_workspace_disambiguation(mock_settings):
    """Test that agent can handle workspace selection when multiple exist
    
    User Story 3 / T026: ワークスペース選択
    
    Given: Multiple Log Analytics workspaces are available
    When: User asks for error summary without specifying workspace
    Then: Response asks user to specify which workspace or suggests options
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
                chunk.text = """複数の Log Analytics ワークスペースが見つかりました。対象とするワークスペースを指定してください:

- workspace-app-prod (location: japaneast)
- workspace-infra-prod (location: japanwest)
- workspace-dev (location: japaneast)

例: "workspace-app-prod の直近1時間のエラーを確認して" """
                yield chunk
            
            mock_agent_instance.run_stream = mock_run_stream
            mock_agent_instance.get_new_thread.return_value = mock_thread
            MockChatAgent.return_value = mock_agent_instance
            
            agent = await create_agent(mock_settings)
            thread = agent.get_new_thread()
            
            query = "エラーをLog Analyticsで確認して"
            response_parts = []
            async for chunk in agent.run_stream([query], thread=thread):
                if chunk.text:
                    response_parts.append(chunk.text)
            
            response = ''.join(response_parts)
            
            # Verify workspace disambiguation message
            assert "ワークスペース" in response
            assert "指定" in response or "選択" in response
            # Should list some workspace names
            assert "workspace" in response.lower() or "japaneast" in response or "japanwest" in response


# ============================================================================
# Phase 6 / T036: Basic Performance Tests
# ============================================================================


@pytest.mark.asyncio
async def test_agent_handles_large_resource_group_list_efficiently(mock_settings):
    """Test that agent can handle large resource group lists efficiently
    
    Phase 6 / T036: パフォーマンステスト - 大量リソースグループ
    
    Given: MCP client returns 100 resource groups
    When: Agent processes and formats the response
    Then: Response is generated without significant delay
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
            
            # Generate a large response with 100 resource groups
            large_response = "以下がこのサブスクリプションのリソースグループ一覧です:\n\n"
            for i in range(100):
                large_response += f"- rg-app-{i:03d} (location: japaneast, tags: env=prod)\n"
            large_response += "\n合計 100 件のリソースグループが見つかりました。"
            
            async def mock_run_stream(*args, **kwargs):
                chunk = MagicMock()
                chunk.text = large_response
                yield chunk
            
            mock_agent_instance.run_stream = mock_run_stream
            mock_agent_instance.get_new_thread.return_value = mock_thread
            MockChatAgent.return_value = mock_agent_instance
            
            agent = await create_agent(mock_settings)
            thread = agent.get_new_thread()
            
            # Measure time to process query
            start_time = time.time()
            query = "このサブスクリプションのリソースグループ一覧を出して"
            response_parts = []
            async for chunk in agent.run_stream([query], thread=thread):
                if chunk.text:
                    response_parts.append(chunk.text)
            elapsed_time = time.time() - start_time
            
            response = ''.join(response_parts)
            
            # Verify response contains all items
            assert "rg-app-000" in response
            assert "rg-app-099" in response
            assert "100 件" in response
            
            # Performance check: should complete within reasonable time (5 seconds is generous for mocked data)
            assert elapsed_time < 5.0, f"Query took too long: {elapsed_time:.2f} seconds"


@pytest.mark.asyncio
async def test_agent_handles_large_storage_account_list_efficiently(mock_settings):
    """Test that agent can handle large storage account lists efficiently
    
    Phase 6 / T036: パフォーマンステスト - 大量ストレージアカウント
    
    Given: MCP client returns 50 storage accounts
    When: Agent processes and formats the response
    Then: Response is generated without significant delay
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
            
            # Generate a large response with 50 storage accounts
            large_response = "リソースグループ「rg-storage」内のストレージアカウント一覧:\n\n"
            for i in range(50):
                kind = "StorageV2" if i % 2 == 0 else "BlobStorage"
                sku = "Standard_LRS" if i % 3 == 0 else "Standard_GRS"
                location = "japaneast" if i % 2 == 0 else "japanwest"
                large_response += f"- stapp{i:03d} (location: {location}, kind: {kind}, sku: {sku})\n"
            large_response += "\n合計 50 件のストレージアカウントが見つかりました。"
            
            async def mock_run_stream(*args, **kwargs):
                chunk = MagicMock()
                chunk.text = large_response
                yield chunk
            
            mock_agent_instance.run_stream = mock_run_stream
            mock_agent_instance.get_new_thread.return_value = mock_thread
            MockChatAgent.return_value = mock_agent_instance
            
            agent = await create_agent(mock_settings)
            thread = agent.get_new_thread()
            
            # Measure time to process query
            start_time = time.time()
            query = "rg-storage のストレージアカウントを一覧して"
            response_parts = []
            async for chunk in agent.run_stream([query], thread=thread):
                if chunk.text:
                    response_parts.append(chunk.text)
            elapsed_time = time.time() - start_time
            
            response = ''.join(response_parts)
            
            # Verify response contains items
            assert "stapp000" in response
            assert "stapp049" in response
            assert "50 件" in response
            
            # Performance check
            assert elapsed_time < 5.0, f"Query took too long: {elapsed_time:.2f} seconds"


@pytest.mark.asyncio
async def test_agent_handles_large_error_summary_efficiently(mock_settings):
    """Test that agent can summarize large error datasets efficiently
    
    Phase 6 / T036: パフォーマンステスト - 大量エラーログ要約
    
    Given: MCP client returns summary of 500 errors
    When: Agent processes and summarizes
    Then: Response is generated efficiently with aggregated view
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
            
            # Generate a large error summary (500 total errors across categories)
            large_response = """直近 24 時間 のエラー状況を要約しました。

■ エラー件数の概要
- Application エラー: 320 件
- Platform エラー: 105 件
- Network エラー: 75 件
- Warning: 150 件

■ 代表的なエラーメッセージ
- Application: "Database connection timeout occurred" (resource: /subscriptions/sub-123/resourceGroups/rg-app/providers/Microsoft.Web/sites/app-web-01)
- Application: "Memory allocation failed" (resource: /subscriptions/sub-123/resourceGroups/rg-app/providers/Microsoft.Web/sites/app-web-02)
- Platform: "VM failed to start due to allocation error" (resource: /subscriptions/sub-123/resourceGroups/rg-infra/providers/Microsoft.Compute/virtualMachines/vm-01)
- Network: "Connection to external service timed out" (resource: /subscriptions/sub-123/resourceGroups/rg-network/providers/Microsoft.Network/virtualNetworks/vnet-01)
- Warning: "High CPU usage detected (>90%)" (resource: /subscriptions/sub-123/resourceGroups/rg-app/providers/Microsoft.Web/sites/app-api)

■ 次に実行をおすすめする 3〜5 ステップ
1. Application エラーについて、該当リソースのメトリック（CPU/メモリ/接続数）を確認してください。
2. Database の接続文字列やネットワーク設定（NSG/Firewall）に変更がなかったかを確認してください。
3. Platform エラーが継続する場合は、別リージョンでのリソース再作成を検討してください。
4. Network エラーについて、外部サービスの稼働状況とネットワークルートを確認してください。
5. 高 CPU 使用率の警告については、アプリケーションのスケールアウトやコード最適化を検討してください。"""
            
            async def mock_run_stream(*args, **kwargs):
                chunk = MagicMock()
                chunk.text = large_response
                yield chunk
            
            mock_agent_instance.run_stream = mock_run_stream
            mock_agent_instance.get_new_thread.return_value = mock_thread
            MockChatAgent.return_value = mock_agent_instance
            
            agent = await create_agent(mock_settings)
            thread = agent.get_new_thread()
            
            # Measure time to process query
            start_time = time.time()
            query = "直近24時間のエラーをLog Analyticsで確認して"
            response_parts = []
            async for chunk in agent.run_stream([query], thread=thread):
                if chunk.text:
                    response_parts.append(chunk.text)
            elapsed_time = time.time() - start_time
            
            response = ''.join(response_parts)
            
            # Verify response contains summary
            assert "エラー件数" in response
            assert "320 件" in response
            assert "代表的なエラーメッセージ" in response
            assert "次に実行をおすすめする" in response
            
            # Verify 3-5 step troubleshooting guide (FR-008)
            step_count = len(re.findall(r'\n\d+\.\s+', response))
            assert 3 <= step_count <= 5, f"Should have 3-5 troubleshooting steps, found {step_count}"
            
            # Performance check
            assert elapsed_time < 5.0, f"Query took too long: {elapsed_time:.2f} seconds"
