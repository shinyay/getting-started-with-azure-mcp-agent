"""Basic package scaffold tests

Note: This test file is minimal for Phase 1 (project scaffold).
The tests verify that the basic package structure is in place.
More comprehensive tests will be added in later phases (Phase 2-6).
"""


def test_project_structure_exists():
    """Test that the basic project files exist"""
    from pathlib import Path
    
    repo_root = Path(__file__).parent.parent.parent
    
    # Check that key files exist
    assert (repo_root / "src" / "azure_mcp_agent" / "__init__.py").exists()
    assert (repo_root / "src" / "azure_mcp_agent" / "agent.py").exists()
    assert (repo_root / "pyproject.toml").exists()
    assert (repo_root / "pytest.ini").exists()
    assert (repo_root / "README.md").exists()
    assert (repo_root / ".gitignore").exists()


def test_package_metadata():
    """Test that basic package metadata is available"""
    # Read pyproject.toml to verify metadata
    from pathlib import Path
    
    repo_root = Path(__file__).parent.parent.parent
    pyproject_path = repo_root / "pyproject.toml"
    
    content = pyproject_path.read_text()
    
    # Check for key metadata
    assert 'name = "azure-mcp-agent"' in content
    assert 'version = "0.1.0"' in content
    assert "azure_mcp_agent" in content  # Package name in some form
