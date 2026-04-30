from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # OpenRouter
    openrouter_api_key: str = Field(..., description="OpenRouter API key")
    openrouter_model: str = Field("openai/gpt-4o-mini", description="OpenRouter model to use")
    openrouter_max_tokens: int = Field(8192, description="Max tokens for AI response")
    openrouter_base_url: str = Field("https://openrouter.ai/api/v1", description="OpenRouter API base URL")
    openrouter_site_url: str = Field("http://localhost:8000", description="App URL for OpenRouter attribution")
    openrouter_app_name: str = Field("Baseera LLM Suggestions Service", description="App name for OpenRouter attribution")

    # Service
    app_env: str = Field("development", description="Runtime environment")
    app_host: str = Field("0.0.0.0")
    app_port: int = Field(8000)
    app_log_level: str = Field("info")

    # Security
    service_api_key: str = Field(..., description="Bearer token for inbound requests")
    # Allow using the same token for service auth and upstream API in development
    allow_shared_api_key: bool = Field(False, description="Allow using the OpenRouter API key as the local service key (development only)")

    # Rate limiting
    rate_limit_rpm: int = Field(30, description="Requests per minute per client")

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @field_validator("openrouter_api_key", "service_api_key", mode="before")
    @classmethod
    def clean_api_key(cls, v: str | None) -> str | None:
        if isinstance(v, str):
            v = v.strip().strip('"').strip("'")
            if v.lower().startswith("bearer "):
                v = v[7:].strip()
        return v


settings = Settings()  # type: ignore[call-arg]
