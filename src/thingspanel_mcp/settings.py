from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DeviceSettings(BaseSettings):
    """
    Settings for the device management tools.
    """

    enabled: bool = Field(
        default=True, description="Whether to enable the device management tools."
    )


class DataSettings(BaseSettings):
    """
    Settings for the data retrieval tools.
    """

    enabled: bool = Field(
        default=True, description="Whether to enable the data retrieval tools."
    )


class AlarmSettings(BaseSettings):
    """
    Settings for the alarm tools.
    """

    enabled: bool = Field(
        default=True, description="Whether to enable the alarm tools."
    )


class ProductSettings(BaseSettings):
    """
    Settings for the product management tools.
    """

    enabled: bool = Field(
        default=True, description="Whether to enable the product management tools."
    )


class ToolSettings(BaseSettings):
    device: DeviceSettings = Field(default_factory=DeviceSettings)
    data: DataSettings = Field(default_factory=DataSettings)
    alarm: AlarmSettings = Field(default_factory=AlarmSettings)
    product: ProductSettings = Field(default_factory=ProductSettings)


class ThingsPanelSettings(BaseSettings):
    model_config: SettingsConfigDict = SettingsConfigDict(
        env_prefix="THINGSPANEL_", env_file=".env", env_nested_delimiter="__"
    )

    url: str = Field(
        default="http://demo.thingspanel.cn/", 
        description="The URL of the ThingsPanel instance."
    )
    api_key: str | None = Field(
        default=None,
        description="A ThingsPanel API key with the necessary permissions to use the tools.",
    )

    tools: ToolSettings = Field(default_factory=ToolSettings)


thingspanel_settings = ThingsPanelSettings() 