from typing import Annotated

from pydantic import AliasChoices, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class GlobalSettings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="forbid",
        secrets_dir="./secrets",
    )

    db_user: Annotated[str, Field(alias="DB_USER")]
    db_host: Annotated[str, Field(alias="DB_HOST")]
    db_port: Annotated[str, Field(alias="DB_PORT")]
    db_name: Annotated[str, Field(alias="DB_NAME")]

    fastapiuser_pswd: Annotated[
        SecretStr,
        Field(validation_alias=AliasChoices("fastapiuser_pswd", "secret_fastapiuser_pswd")),
    ]

    @property
    def get_db_url(self) -> str:
        return f"postgresql://{self.db_user}:{self.fastapiuser_pswd.get_secret_value()}@{self.db_host}:{self.db_port}/{self.db_name}"
