import pytest
from seekdb_mcp.server import _init_seekdb


@pytest.fixture(autouse=True)
def init_seekdb():
    """Automatically initialize seekdb client before all tests."""
    _init_seekdb()
