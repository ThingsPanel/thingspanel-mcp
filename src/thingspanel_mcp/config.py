"""Configuration for ThingsPanel and ThingsVis API access."""
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class Config:
    def __init__(self):
        self.base_url = "http://demo.thingspanel.cn"
        self.api_prefix = "/api/v1"
        self.thingsvis_base_url = "http://localhost:8000"
        self.thingsvis_api_prefix = "/api/v1"
        self.profiles: Dict[str, Dict[str, Optional[str]]] = {}
        self.load_config()

    @property
    def api_key(self) -> Optional[str]:
        """Backward-compatible alias for the default ThingsPanel API key."""
        return self.get_profile("default").get("thingspanel_api_key")

    @api_key.setter
    def api_key(self, value: Optional[str]) -> None:
        self.profiles.setdefault("default", {})["thingspanel_api_key"] = value

    @property
    def token(self) -> Optional[str]:
        return self.get_profile("default").get("thingspanel_token")

    def get_profile(self, name: str = "default") -> Dict[str, Optional[str]]:
        profile = self.profiles.get(name)
        if profile is None:
            raise KeyError(f"未知认证配置 profile: {name}")
        return profile

    def load_config(self):
        """Load base URLs and identity credentials without logging secret values.

        Config files may use the legacy ``api_key`` field or a ``profiles`` mapping:

        {"profiles": {"superadmin": {"thingspanel_token": "...",
        "thingsvis_token": "..."}}}
        """
        config_path = os.environ.get(
            "THINGSPANEL_CONFIG_PATH", str(Path.home() / ".thingspanel" / "config.json")
        )
        config_data: Dict[str, Any] = {}
        try:
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as config_file:
                    loaded = json.load(config_file)
                    if isinstance(loaded, dict):
                        config_data = loaded
        except (OSError, ValueError, TypeError) as exc:
            logger.warning("ThingsPanel config file could not be loaded: %s", exc.__class__.__name__)

        self.base_url = (
            os.environ.get("THINGSPANEL_BASE_URL")
            or config_data.get("base_url")
            or "http://demo.thingspanel.cn"
        ).rstrip("/")
        self.api_prefix = (
            os.environ.get("THINGSPANEL_API_PREFIX")
            or config_data.get("api_prefix")
            or "/api/v1"
        ).rstrip("/") or "/"
        self.thingsvis_base_url = (
            os.environ.get("THINGSVIS_BASE_URL")
            or config_data.get("thingsvis_base_url")
            or "http://localhost:8000"
        ).rstrip("/")
        self.thingsvis_api_prefix = (
            os.environ.get("THINGSVIS_API_PREFIX")
            or config_data.get("thingsvis_api_prefix")
            or "/api/v1"
        ).rstrip("/") or "/"

        profiles: Dict[str, Dict[str, Optional[str]]] = {}
        raw_profiles = config_data.get("profiles", {})
        if isinstance(raw_profiles, dict):
            for name, values in raw_profiles.items():
                if isinstance(name, str) and name and isinstance(values, dict):
                    profiles[name] = self._normalize_profile(values)

        legacy_default = profiles.setdefault("default", {})
        if config_data.get("api_key"):
            legacy_default.setdefault("thingspanel_api_key", str(config_data["api_key"]))

        # Environment values override the default profile; no secret is printed.
        env_fields = {
            "THINGSPANEL_TOKEN": "thingspanel_token",
            "THINGSPANEL_API_KEY": "thingspanel_api_key",
            "THINGSPANEL_REFRESH_TOKEN": "thingspanel_refresh_token",
            "THINGSVIS_TOKEN": "thingsvis_token",
            "THINGSVIS_REFRESH_TOKEN": "thingsvis_refresh_token",
            "THINGSVIS_INTERNAL_SECRET": "thingsvis_internal_secret",
            "THINGSVIS_OPEN_API_KEY": "thingsvis_open_api_key",
        }
        for env_name, field in env_fields.items():
            if os.environ.get(env_name):
                legacy_default[field] = os.environ[env_name]

        # Named profiles can be supplied as THINGSPANEL_PROFILE_<NAME>_<FIELD>.
        env_suffixes = sorted({
            "TOKEN": "thingspanel_token",
            "API_KEY": "thingspanel_api_key",
            "THINGSVIS_TOKEN": "thingsvis_token",
            "THINGSVIS_REFRESH_TOKEN": "thingsvis_refresh_token",
            "THINGSPANEL_REFRESH_TOKEN": "thingspanel_refresh_token",
        }.items(), key=lambda item: len(item[0]), reverse=True)
        for env_name, value in os.environ.items():
            prefix = "THINGSPANEL_PROFILE_"
            upper_name = env_name.upper()
            if not upper_name.startswith(prefix):
                continue
            remainder = upper_name[len(prefix):]
            for suffix, field in env_suffixes:
                marker = "_" + suffix
                if remainder.endswith(marker):
                    profile_name = remainder[:-len(marker)]
                    if profile_name and value:
                        profiles.setdefault(profile_name.lower(), {})[field] = value
                    break

        self.profiles = profiles

    @staticmethod
    def _normalize_profile(values: Dict[str, Any]) -> Dict[str, Optional[str]]:
        aliases = {
            "token": "thingspanel_token",
            "api_key": "thingspanel_api_key",
            "thingspanel_token": "thingspanel_token",
            "thingspanel_api_key": "thingspanel_api_key",
            "thingspanel_refresh_token": "thingspanel_refresh_token",
            "thingsvis_token": "thingsvis_token",
            "thingsvis_access_token": "thingsvis_token",
            "thingsvis_refresh_token": "thingsvis_refresh_token",
            "thingsvis_internal_secret": "thingsvis_internal_secret",
            "thingsvis_open_api_key": "thingsvis_open_api_key",
        }
        normalized: Dict[str, Optional[str]] = {}
        for key, value in values.items():
            target = aliases.get(key)
            if target and value is not None:
                normalized[target] = str(value)
        return normalized

    def is_configured(self) -> bool:
        """The MCP server is usable when any profile has an API credential."""
        return any(
            profile.get("thingspanel_token")
            or profile.get("thingspanel_api_key")
            or profile.get("thingsvis_token")
            or profile.get("thingsvis_internal_secret")
            or profile.get("thingsvis_open_api_key")
            for profile in self.profiles.values()
        )


config = Config()
