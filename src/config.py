from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = Field(
        default="sqlite:///./job_tracker.db",
        validation_alias="DATABASE_URL",
    )

    ollama_model: str = Field(
        default="llama3",
        validation_alias="OLLAMA_MODEL",
    )

    @property
    def DATABASE_URL(self) -> str:
        return self.database_url

    @property
    def OLLAMA_MODEL(self) -> str:
        return self.ollama_model

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        extra="ignore",
    )


settings = Settings()
