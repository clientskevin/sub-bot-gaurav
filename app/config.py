import os
from typing import Literal, Optional

from pydantic_settings import SettingsConfigDict, YamlConfigSettingsSource
from pydantic_settings_yaml import YamlBaseSettings

default_file = "secrets/config.yaml"
dev_file = "secrets/config.dev.yaml"
sample_file = "secrets/config.sample.yaml"

# take dev if it exists, else the default, else sample
if os.path.exists(dev_file):
    selected_config = dev_file
elif os.path.exists(default_file):
    selected_config = default_file
else:
    selected_config = sample_file


class ConfigSettings(YamlBaseSettings):
    """Application configuration settings."""

    API_ID: int
    API_HASH: str
    BOT_TOKEN: str

    DATABASE_NAME: str = "tg_bot"
    DATABASE_URL: Optional[str] = None

    OWNER_ID: int
    LOG_CHANNEL: int

    LOG_LEVEL: str = "INFO"

    ENV: Literal["dev", "prod"] = "dev"

    @property
    def is_prod(self) -> bool:
        return self.ENV == "prod"

    model_config = SettingsConfigDict(
        yaml_file=selected_config,
        extra="ignore",
        secrets_dir="secrets",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            YamlConfigSettingsSource(settings_cls),
            file_secret_settings,
        )


configs = ConfigSettings()  # type: ignore
