"""
Application configuration settings.
"""
import os
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

class Settings(BaseSettings):
    OPENAI_API_KEY: str = Field(
        default=os.getenv("OPENAI_API_KEY", ""),
        description="OpenAI API Key"
    )
    LLM_MODEL: str = Field(
        default=os.getenv("LLM_MODEL", "gpt-4o-mini"),
        description="LLM Model Name"
    )
    GRAFANA_URL: str = Field(
        default=os.getenv("GRAFANA_URL", "http://localhost:3000"),
        description="Grafana API URL"
    )
    GRAFANA_API_KEY: str = Field(
        default=os.getenv("GRAFANA_API_KEY", ""),
        description="Grafana API Key"
    )
    SMTP_SERVER: str = Field(
        default=os.getenv("SMTP_SERVER", ""),
        description="SMTP Server Address"
    )
    SMTP_PORT: int = Field(
        default=int(os.getenv("SMTP_PORT", "587")),
        description="SMTP Port"
    )
    SMTP_USERNAME: str = Field(
        default=os.getenv("SMTP_USERNAME", ""),
        description="SMTP username)"
    )
    SMTP_PASSWORD: str = Field(
        default=os.getenv("SMTP_PASSWORD", ""),
        description="SMTP password"
    )
    ALERT_RECIPIENTS: str = Field(
        default=os.getenv("ALERT_RECIPIENTS", ""),
        description="alert recipients"
    )
    LOG_LEVEL: str = Field(
        default=os.getenv("LOG_LEVEL", "INFO"),
        description="logging level"
    )
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()