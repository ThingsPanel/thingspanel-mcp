"""
A client for the ThingsPanel API.
"""

import json
from typing import Any, Dict, List, Optional

import httpx

from .settings import thingspanel_settings


class ThingsPanelError(Exception):
    """
    An error returned by the ThingsPanel API.
    """
    pass


class ApiKeyAuth(httpx.Auth):
    """
    Authentication using x-api-key header.
    """
    def __init__(self, api_key: str):
        self.api_key = api_key

    def auth_flow(self, request):
        request.headers["x-api-key"] = self.api_key
        yield request


class ThingsPanelClient:
    """
    Client for ThingsPanel API.
    """
    def __init__(self, url: str, api_key: str | None = None) -> None:
        self.url = url.rstrip('/')
        auth = ApiKeyAuth(api_key) if api_key is not None else None
        self.client = httpx.AsyncClient(base_url=self.url, auth=auth)

    async def get(self, path: str, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """
        Make a GET request to the ThingsPanel API.
        """
        response = await self.client.get(path, params=params)
        if response.status_code >= 400:
            raise ThingsPanelError(f"Error {response.status_code}: {response.text}")
        return response.json()

    async def post(self, path: str, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a POST request to the ThingsPanel API.
        """
        response = await self.client.post(path, json=json_data)
        if response.status_code >= 400:
            raise ThingsPanelError(f"Error {response.status_code}: {response.text}")
        return response.json()

    async def put(self, path: str, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a PUT request to the ThingsPanel API.
        """
        response = await self.client.put(path, json=json_data)
        if response.status_code >= 400:
            raise ThingsPanelError(f"Error {response.status_code}: {response.text}")
        return response.json()

    async def delete(self, path: str) -> Dict[str, Any]:
        """
        Make a DELETE request to the ThingsPanel API.
        """
        response = await self.client.delete(path)
        if response.status_code >= 400:
            raise ThingsPanelError(f"Error {response.status_code}: {response.text}")
        return response.json()

    # Device APIs
    async def list_devices(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        List devices.
        """
        return await self.get("/api/v1/device/list", params=params)

    async def get_device(self, device_id: str) -> Dict[str, Any]:
        """
        Get device by ID.
        """
        return await self.get(f"/api/v1/device/detail/{device_id}")

    async def create_device(self, device_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new device.
        """
        return await self.post("/api/v1/device/create", json_data=device_data)

    async def update_device(self, device_id: str, device_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing device.
        """
        return await self.put(f"/api/v1/device/update/{device_id}", json_data=device_data)

    async def delete_device(self, device_id: str) -> Dict[str, Any]:
        """
        Delete a device.
        """
        return await self.delete(f"/api/v1/device/delete/{device_id}")

    # Product APIs
    async def list_products(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        List products.
        """
        return await self.get("/api/v1/product", params=params)

    # Data APIs
    async def get_device_data(self, device_id: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get data for a device.
        """
        return await self.get(f"/api/v1/device/map/telemetry/{device_id}", params=params)

    # Command APIs
    async def send_command(self, device_id: str, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a command to a device.
        """
        return await self.post(f"/api/v1/device/model/commands/{device_id}", json_data=command_data) 