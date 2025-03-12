import os
import pytest
from unittest.mock import patch

from thingspanel_mcp.settings import ThingsPanelSettings


@pytest.fixture
def mock_settings():
    """
    Fixture that provides a mocked settings object for tests.
    """
    with patch('thingspanel_mcp.settings.ThingsPanelSettings') as mock_settings:
        test_settings = ThingsPanelSettings(
            url="http://test.thingspanel.cn/",
            api_key="test_api_key"
        )
        mock_settings.return_value = test_settings
        yield test_settings


@pytest.fixture
def mock_environment(monkeypatch):
    """
    Fixture that sets up test environment variables.
    """
    monkeypatch.setenv("THINGSPANEL_URL", "http://test.thingspanel.cn/")
    monkeypatch.setenv("THINGSPANEL_API_KEY", "test_api_key")
    yield 