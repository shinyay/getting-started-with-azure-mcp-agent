"""Smoke tests for Phase 2 foundational components

These tests verify that the basic infrastructure (config, prompts, mcp_client, agent, cli)
can be imported and has the expected structure.
"""

from pathlib import Path

# Path to the source code
repo_root = Path(__file__).parent.parent.parent
src_path = repo_root / "src"


def test_config_module_imports():
    """Test that config module can be imported and has expected exports"""
    config_path = src_path / "azure_mcp_agent" / "config.py"
    assert config_path.exists()
    
    # Check that key components are defined
    content = config_path.read_text()
    assert "class Settings" in content
    assert "def get_settings" in content
    assert "def validate_mcp_server_available" in content
    assert "field(default_factory=" in content  # Verify we're using field for mutable defaults


def test_prompts_module_imports():
    """Test that prompts module can be imported and has expected exports"""
    prompts_path = src_path / "azure_mcp_agent" / "prompts.py"
    assert prompts_path.exists()
    
    # Check that key components are defined
    content = prompts_path.read_text()
    assert "BASE_SYSTEM_PROMPT" in content
    assert "def get_system_prompt" in content
    assert "def get_error_message" in content
    assert "def get_success_message" in content


def test_system_prompt_is_japanese():
    """Test that system prompt contains Japanese instructions"""
    prompts_path = src_path / "azure_mcp_agent" / "prompts.py"
    content = prompts_path.read_text()
    
    # Check for key Japanese phrases in BASE_SYSTEM_PROMPT
    assert "Azure" in content
    assert "日本語" in content
    assert "読み取り専用" in content


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
    assert "create_agent_sync" in content
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
    config_path = src_path / "azure_mcp_agent" / "config.py"
    content = config_path.read_text()
    
    # Verify Settings dataclass structure
    assert "@dataclass" in content
    assert "class Settings:" in content
    assert "model_name: str" in content
    assert "api_base: str" in content
    assert "api_key: str" in content
    assert 'mcp_command: str = "npx"' in content
    assert "field(default_factory=lambda:" in content
    assert "--read-only" in content


def test_error_message_templates():
    """Test that error message templates work correctly"""
    prompts_path = src_path / "azure_mcp_agent" / "prompts.py"
    content = prompts_path.read_text()
    
    # Verify error message templates are defined
    assert "ERROR_MESSAGES = {" in content
    assert "no_resource_groups" in content
    assert "resource_group_not_found" in content
    assert "mcp_connection_error" in content
    # Verify improved error handling
    assert "if error_type in ERROR_MESSAGES:" in content
    assert "if 'error' not in kwargs:" in content


def test_success_message_templates():
    """Test that success message templates work correctly"""
    prompts_path = src_path / "azure_mcp_agent" / "prompts.py"
    content = prompts_path.read_text()
    
    # Verify success message templates are defined
    assert "SUCCESS_MESSAGES = {" in content
    assert "resource_groups_found" in content
    assert "storage_accounts_found" in content
    # Verify KeyError is raised for unknown message types
    assert "raise KeyError" in content
    assert "Unknown success message type" in content


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
