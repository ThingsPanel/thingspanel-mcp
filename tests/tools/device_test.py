import json
import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from thingspanel_mcp.tools.device import (
    DeviceListRequest,
    DeviceRequest,
    DeviceCreateRequest,
    DeviceUpdateRequest,
    list_devices,
    get_device,
    create_device,
    update_device,
    delete_device,
)


@pytest.fixture
def mock_client():
    with patch('thingspanel_mcp.tools.device.ThingsPanelClient') as mock:
        client_instance = AsyncMock()
        mock.return_value = client_instance
        yield client_instance


@pytest.mark.asyncio
async def test_list_devices(mock_client):
    # Prepare test data
    mock_client.list_devices.return_value = {
        "code": 200,
        "data": {
            "list": [
                {"device_id": "device1", "name": "Test Device 1"},
                {"device_id": "device2", "name": "Test Device 2"}
            ],
            "total": 2
        },
        "msg": "success"
    }
    
    # Call the function
    result = await list_devices(DeviceListRequest(limit=10, offset=0))
    
    # Assert
    result_dict = json.loads(result)
    assert result_dict["code"] == 200
    assert len(result_dict["data"]["list"]) == 2
    assert result_dict["data"]["total"] == 2
    mock_client.list_devices.assert_called_once_with({"limit": 10, "offset": 0})


@pytest.mark.asyncio
async def test_get_device(mock_client):
    # Prepare test data
    mock_client.get_device.return_value = {
        "code": 200,
        "data": {"device_id": "device1", "name": "Test Device 1"},
        "msg": "success"
    }
    
    # Call the function
    result = await get_device(DeviceRequest(device_id="device1"))
    
    # Assert
    result_dict = json.loads(result)
    assert result_dict["code"] == 200
    assert result_dict["data"]["device_id"] == "device1"
    mock_client.get_device.assert_called_once_with("device1") 