"""Smoke tests for Phase 2 foundational components

These tests verify that the basic infrastructure (config, prompts, mcp_client, agent, cli)
can be imported and has the expected structure.
"""

import sys
from pathlib import Path
import importlib.util

# Workaround for the tests/azure_mcp_agent directory name collision
# Directly load modules from src to avoid import confusion
repo_root = Path(__file__).parent.parent.parent
src_path = repo_root / "src"


def import_from_src(module_name):
    """Import a module directly from src to avoid test directory conflicts"""
    module_path = src_path / "azure_mcp_agent" / f"{module_name}.py"
    spec = importlib.util.spec_from_file_location(f"azure_mcp_agent.{module_name}", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_config_module_imports():
    """Test that config module can be imported and has expected exports"""
    config = import_from_src("config")
    
    assert hasattr(config, 'Settings')
    assert hasattr(config, 'get_settings')
    assert hasattr(config, 'validate_mcp_server_available')


def test_prompts_module_imports():
    """Test that prompts module can be imported and has expected exports"""
    prompts = import_from_src("prompts")
    
    assert hasattr(prompts, 'BASE_SYSTEM_PROMPT')
    assert hasattr(prompts, 'get_system_prompt')
    assert hasattr(prompts, 'get_error_message')
    assert hasattr(prompts, 'get_success_message')


def test_system_prompt_is_japanese():
    """Test that system prompt contains Japanese instructions"""
    prompts = import_from_src("prompts")
    
    prompt = prompts.get_system_prompt()
    assert isinstance(prompt, str)
    assert len(prompt) > 0
    # Check for key Japanese phrases
    assert "Azure" in prompt
    assert "日本語" in prompt or "読み取り専用" in prompt


def test_mcp_client_module_structure():
    """Test that mcp_client module has expected structure"""
    mcp_client_path = src_path / "azure_mcp_agent" / "mcp_client.py"
    assert mcp_client_path.exists()
    
    # Check that key functions are defined
    content = mcp_client_path.read_text()
    assert "def create_azure_mcp_tool" in content
    assert "def validate_mcp_connection" in content
    assert "MCPStdioTool" in content


def test_agent_module_structure():
    """Test that agent module has expected structure"""
    agent_path = src_path / "azure_mcp_agent" / "agent.py"
    assert agent_path.exists()
    
    # Check that key functions are defined
    content = agent_path.read_text()
    assert "async def create_agent" in content
    assert "def create_agent_sync" in content or "create_agent_sync" in content
    assert "ChatAgent" in content


def test_cli_module_structure():
    """Test that cli module has expected structure"""
    cli_path = src_path / "azure_mcp_agent" / "cli.py"
    assert cli_path.exists()
    
    # Check that key functions are defined
    content = cli_path.read_text()
    assert "def main" in content
    assert "def print_banner" in content
    assert "async def run_interactive_session" in content


def test_settings_dataclass_structure():
    """Test that Settings dataclass has expected fields"""
    config = import_from_src("config")
    
    # Create a minimal settings object
    settings = config.Settings(
        model_name="test-model",
        api_base="https://test.example.com",
        api_key="test-key"
    )
    
    assert settings.model_name == "test-model"
    assert settings.api_base == "https://test.example.com"
    assert settings.api_key == "test-key"
    assert settings.mcp_command == "npx"
    assert settings.mcp_args is not None
    assert len(settings.mcp_args) > 0
    assert "--read-only" in settings.mcp_args


def test_error_message_templates():
    """Test that error message templates work correctly"""
    prompts = import_from_src("prompts")
    
    # Test basic error message
    msg = prompts.get_error_message("no_resource_groups")
    assert isinstance(msg, str)
    assert len(msg) > 0
    
    # Test parameterized error message
    msg = prompts.get_error_message("resource_group_not_found", rg_name="test-rg")
    assert "test-rg" in msg


def test_success_message_templates():
    """Test that success message templates work correctly"""
    prompts = import_from_src("prompts")
    
    msg = prompts.get_success_message("resource_groups_found", count=5)
    assert isinstance(msg, str)
    assert "5" in msg


def test_new_files_exist():
    """Test that all Phase 2 files have been created"""
    expected_files = [
        src_path / "azure_mcp_agent" / "config.py",
        src_path / "azure_mcp_agent" / "mcp_client.py",
        src_path / "azure_mcp_agent" / "prompts.py",
        src_path / "azure_mcp_agent" / "agent.py",
        src_path / "azure_mcp_agent" / "cli.py",
        src_path / "azure_mcp_agent" / "main.py",
    ]
    
    for file_path in expected_files:
        assert file_path.exists(), f"Missing file: {file_path}"
