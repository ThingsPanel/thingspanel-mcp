import os
import pytest
from thingspanel_mcp.settings import ThingsPanelSettings, DeviceSettings, DataSettings


def test_default_settings():
    """Test default settings values."""
    settings = ThingsPanelSettings()
    assert settings.url == "http://demo.thingspanel.cn/"
    assert settings.api_key is None
    assert settings.tools.device.enabled is True
    assert settings.tools.data.enabled is True
    assert settings.tools.alarm.enabled is True
    assert settings.tools.product.enabled is True


def test_settings_override_from_env(monkeypatch):
    """Test settings values can be overridden from environment variables."""
    test_url = "http://test.thingspanel.local/"
    test_api_key = "test_api_key_123"
    
    monkeypatch.setenv("THINGSPANEL_URL", test_url)
    monkeypatch.setenv("THINGSPANEL_API_KEY", test_api_key)
    monkeypatch.setenv("THINGSPANEL_TOOLS__DEVICE__ENABLED", "false")
    
    settings = ThingsPanelSettings()
    assert settings.url == test_url
    assert settings.api_key == test_api_key
    assert settings.tools.device.enabled is False
    assert settings.tools.data.enabled is True  # Default value


def test_tool_settings():
    """Test tool-specific settings."""
    device_settings = DeviceSettings(enabled=False)
    assert device_settings.enabled is False
    
    data_settings = DataSettings(enabled=False)
    assert data_settings.enabled is False 