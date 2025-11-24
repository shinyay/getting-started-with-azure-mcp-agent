"""CLI-level tests for Azure Resource Guide Agent

Tests for User Story 1: CLI interaction with resource group listing
Tests verify end-to-end CLI behavior with mocked agent.
"""

import sys
from pathlib import Path

# Ensure src is in path before any imports
repo_root = Path(__file__).parent.parent.parent
src_path = repo_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from io import StringIO

# Import CLI module
import azure_mcp_agent.cli


@pytest.fixture
def mock_cli_settings():
    """Fixture for mock CLI settings"""
    settings = MagicMock()
    settings.mcp_command = "npx"
    return settings


@pytest.mark.asyncio
async def test_cli_lists_resource_groups(mock_cli_settings):
    """Test CLI flow for resource group listing query
    
    User Story 1 / T013: CLI レベルのテスト
    
    Given: CLI is running with mocked agent
    When: User enters "このサブスクリプションのリソースグループ一覧を出して"
    Then: CLI displays RG names and locations without errors
    """
    run_interactive_session = azure_mcp_agent.cli.run_interactive_session
    
    # Mock agent response
    expected_rg_output = """以下がこのサブスクリプションのリソースグループ一覧です:

- rg-test-1 (location: japaneast)
- rg-test-2 (location: japanwest)

合計 2 件のリソースグループが見つかりました。"""
    
    with patch('azure_mcp_agent.cli.get_settings') as mock_get_settings, \
         patch('azure_mcp_agent.cli.validate_mcp_server_available') as mock_validate, \
         patch('azure_mcp_agent.cli.create_agent', new_callable=AsyncMock) as mock_create_agent, \
         patch('builtins.input') as mock_input, \
         patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        
        # Setup mocks
        mock_get_settings.return_value = mock_cli_settings
        mock_validate.return_value = True
        
        # Mock agent
        mock_agent = MagicMock()
        mock_thread = MagicMock()
        mock_agent.get_new_thread.return_value = mock_thread
        
        # Mock streaming response
        async def mock_run_stream(messages, thread):
            chunk = MagicMock()
            chunk.text = expected_rg_output
            yield chunk
        
        mock_agent.run_stream = mock_run_stream
        mock_create_agent.return_value = mock_agent
        
        # Mock user input (query, then exit)
        mock_input.side_effect = [
            "このサブスクリプションのリソースグループ一覧を出して",
            "exit"
        ]
        
        # Run CLI session
        exit_code = await run_interactive_session()
        
        # Verify successful execution
        assert exit_code == 0, "CLI should exit successfully"
        
        # Verify output contains expected content
        output = mock_stdout.getvalue()
        assert "rg-test-1" in output, "Expected resource group name in output"
        
        # Verify no traceback or error messages
        assert "Traceback" not in output
        assert "Error" not in output and "エラー" not in output


@pytest.mark.asyncio
async def test_cli_handles_empty_input(mock_cli_settings):
    """Test that CLI handles empty input gracefully
    
    User Story 1 / T013: エッジケーステスト
    
    Given: CLI is running
    When: User enters empty lines
    Then: CLI continues without errors
    """
    run_interactive_session = azure_mcp_agent.cli.run_interactive_session
    
    with patch('azure_mcp_agent.cli.get_settings') as mock_get_settings, \
         patch('azure_mcp_agent.cli.validate_mcp_server_available') as mock_validate, \
         patch('azure_mcp_agent.cli.create_agent', new_callable=AsyncMock) as mock_create_agent, \
         patch('builtins.input') as mock_input:
        
        mock_get_settings.return_value = mock_cli_settings
        mock_validate.return_value = True
        
        mock_agent = MagicMock()
        mock_thread = MagicMock()
        mock_agent.get_new_thread.return_value = mock_thread
        
        async def mock_run_stream(messages, thread):
            chunk = MagicMock()
            chunk.text = "テスト応答"
            yield chunk
        
        mock_agent.run_stream = mock_run_stream
        mock_create_agent.return_value = mock_agent
        
        # Empty input, then exit
        mock_input.side_effect = ["", "", "exit"]
        
        exit_code = await run_interactive_session()
        assert exit_code == 0


@pytest.mark.asyncio
async def test_cli_handles_configuration_error():
    """Test that CLI handles missing configuration gracefully
    
    User Story 1 / T013: エラーハンドリング
    
    Given: Required environment variables are not set
    When: CLI attempts to start
    Then: User sees clear error message in Japanese
    """
    run_interactive_session = azure_mcp_agent.cli.run_interactive_session
    
    with patch('azure_mcp_agent.cli.get_settings') as mock_get_settings, \
         patch('sys.stderr', new_callable=StringIO) as mock_stderr:
        
        # Simulate configuration error
        mock_get_settings.side_effect = ValueError(
            "必須の環境変数が設定されていません: GITHUB_MODEL_NAME or AZURE_OPENAI_MODEL_NAME"
        )
        
        exit_code = await run_interactive_session()
        
        # Verify error exit code
        assert exit_code == 1
        
        # Verify error message is displayed
        error_output = mock_stderr.getvalue()
        assert "設定エラー" in error_output
        assert "環境変数" in error_output


@pytest.mark.asyncio
async def test_cli_exits_on_quit_command(mock_cli_settings):
    """Test that CLI exits cleanly on quit command
    
    User Story 1 / T013: 基本動作
    
    Given: CLI is running
    When: User enters "quit" or "exit" or "終了"
    Then: CLI exits with code 0
    """
    run_interactive_session = azure_mcp_agent.cli.run_interactive_session
    
    # Test each exit command
    for exit_cmd in ["quit", "exit", "終了"]:
        with patch('azure_mcp_agent.cli.get_settings') as mock_get_settings, \
             patch('azure_mcp_agent.cli.validate_mcp_server_available') as mock_validate, \
             patch('azure_mcp_agent.cli.create_agent', new_callable=AsyncMock) as mock_create_agent, \
             patch('builtins.input') as mock_input:
            
            mock_get_settings.return_value = mock_cli_settings
            mock_validate.return_value = True
            
            mock_agent = MagicMock()
            mock_thread = MagicMock()
            mock_agent.get_new_thread.return_value = mock_thread
            mock_create_agent.return_value = mock_agent
            
            mock_input.return_value = exit_cmd
            
            exit_code = await run_interactive_session()
            assert exit_code == 0, f"CLI should exit cleanly with '{exit_cmd}' command"


def test_cli_main_function_exists():
    """Test that main() function exists and is callable
    
    User Story 1 / T013: 構造テスト
    """
    main = azure_mcp_agent.cli.main
    
    # Verify main function exists
    assert callable(main)
    
    # Verify it's the entry point
    with patch('azure_mcp_agent.cli.asyncio.run') as mock_asyncio_run:
        mock_asyncio_run.return_value = 0
        
        with patch('azure_mcp_agent.cli.print_banner'):
            result = main()
            
            # Verify asyncio.run was called and result is correct
            assert mock_asyncio_run.called
            assert result == 0


# ============================================================================
# User Story 2: Storage Account Listing CLI Tests
# ============================================================================


@pytest.mark.asyncio
async def test_cli_lists_storage_accounts_in_resource_group(mock_cli_settings):
    """Test CLI flow for storage account listing query with resource group
    
    User Story 2 / T020: CLI レベルのテスト - ストレージアカウント一覧
    
    Given: CLI is running with mocked agent
    When: User enters "<RG名> のストレージアカウントを一覧して"
    Then: CLI displays storage account names, locations, kinds, and SKUs without errors
    """
    run_interactive_session = azure_mcp_agent.cli.run_interactive_session
    
    # Mock agent response
    expected_storage_output = """リソースグループ「rg-test」内のストレージアカウント一覧:

- sttest001 (location: japaneast, kind: StorageV2, sku: Standard_LRS)
- sttest002 (location: japanwest, kind: BlobStorage, sku: Standard_GRS)

合計 2 件のストレージアカウントが見つかりました。"""
    
    with patch('azure_mcp_agent.cli.get_settings') as mock_get_settings, \
         patch('azure_mcp_agent.cli.validate_mcp_server_available') as mock_validate, \
         patch('azure_mcp_agent.cli.create_agent', new_callable=AsyncMock) as mock_create_agent, \
         patch('builtins.input') as mock_input, \
         patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        
        # Setup mocks
        mock_get_settings.return_value = mock_cli_settings
        mock_validate.return_value = True
        
        # Mock agent
        mock_agent = MagicMock()
        mock_thread = MagicMock()
        mock_agent.get_new_thread.return_value = mock_thread
        
        # Mock streaming response
        async def mock_run_stream(messages, thread):
            chunk = MagicMock()
            chunk.text = expected_storage_output
            yield chunk
        
        mock_agent.run_stream = mock_run_stream
        mock_create_agent.return_value = mock_agent
        
        # Mock user input (query, then exit)
        mock_input.side_effect = [
            "rg-test のストレージアカウントを一覧して",
            "exit"
        ]
        
        # Run CLI session
        exit_code = await run_interactive_session()
        
        # Verify successful execution
        assert exit_code == 0, "CLI should exit successfully"
        
        # Verify output contains expected content
        output = mock_stdout.getvalue()
        assert "sttest001" in output, "Expected storage account name in output"
        assert "StorageV2" in output, "Expected kind in output"
        assert "Standard_LRS" in output, "Expected SKU in output"
        
        # Verify no traceback or error messages
        assert "Traceback" not in output
        assert "Error" not in output and "エラー" not in output


@pytest.mark.asyncio
async def test_cli_handles_nonexistent_resource_group_for_storage(mock_cli_settings):
    """Test that CLI handles storage account queries for non-existent resource groups
    
    User Story 2 / T020: エッジケーステスト
    
    Given: CLI is running
    When: User asks for storage accounts in a non-existent RG
    Then: CLI displays clear error message in Japanese
    """
    run_interactive_session = azure_mcp_agent.cli.run_interactive_session
    
    error_response = "指定されたリソースグループ「rg-invalid」が見つかりませんでした。リソースグループ名を確認してください。"
    
    with patch('azure_mcp_agent.cli.get_settings') as mock_get_settings, \
         patch('azure_mcp_agent.cli.validate_mcp_server_available') as mock_validate, \
         patch('azure_mcp_agent.cli.create_agent', new_callable=AsyncMock) as mock_create_agent, \
         patch('builtins.input') as mock_input, \
         patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        
        mock_get_settings.return_value = mock_cli_settings
        mock_validate.return_value = True
        
        mock_agent = MagicMock()
        mock_thread = MagicMock()
        mock_agent.get_new_thread.return_value = mock_thread
        
        async def mock_run_stream(messages, thread):
            chunk = MagicMock()
            chunk.text = error_response
            yield chunk
        
        mock_agent.run_stream = mock_run_stream
        mock_create_agent.return_value = mock_agent
        
        mock_input.side_effect = [
            "rg-invalid のストレージアカウントを一覧して",
            "exit"
        ]
        
        exit_code = await run_interactive_session()
        assert exit_code == 0
        
        output = mock_stdout.getvalue()
        assert "見つかりませんでした" in output, "Expected error message in output"
        assert "リソースグループ" in output, "Expected RG mention in output"


@pytest.mark.asyncio
async def test_cli_handles_empty_storage_accounts_in_rg(mock_cli_settings):
    """Test that CLI handles resource groups with no storage accounts
    
    User Story 2 / T020: エッジケーステスト
    
    Given: CLI is running
    When: User asks for storage accounts in an RG with none
    Then: CLI displays friendly message in Japanese
    """
    run_interactive_session = azure_mcp_agent.cli.run_interactive_session
    
    empty_response = "リソースグループ「rg-empty」にはストレージアカウントが見つかりませんでした。"
    
    with patch('azure_mcp_agent.cli.get_settings') as mock_get_settings, \
         patch('azure_mcp_agent.cli.validate_mcp_server_available') as mock_validate, \
         patch('azure_mcp_agent.cli.create_agent', new_callable=AsyncMock) as mock_create_agent, \
         patch('builtins.input') as mock_input, \
         patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        
        mock_get_settings.return_value = mock_cli_settings
        mock_validate.return_value = True
        
        mock_agent = MagicMock()
        mock_thread = MagicMock()
        mock_agent.get_new_thread.return_value = mock_thread
        
        async def mock_run_stream(messages, thread):
            chunk = MagicMock()
            chunk.text = empty_response
            yield chunk
        
        mock_agent.run_stream = mock_run_stream
        mock_create_agent.return_value = mock_agent
        
        mock_input.side_effect = [
            "rg-empty のストレージアカウントを一覧して",
            "exit"
        ]
        
        exit_code = await run_interactive_session()
        assert exit_code == 0
        
        output = mock_stdout.getvalue()
        assert "ストレージアカウント" in output
        assert "見つかりませんでした" in output or "存在しません" in output
