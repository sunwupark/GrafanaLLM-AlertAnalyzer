"""
Application configuration settings.
"""
import os
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import agentops

load_dotenv()

import operator
from typing import Sequence, Annotated
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage

# 상태 정의
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]  # 메시지
    next: str  # 다음으로 라우팅할 에이전트

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
    GITHUB_TOKEN: str = Field(
        default=os.getenv("GITHUB_TOKEN", ""),
        description="GitHub Personal Access Token"
    )
    GITHUB_REPO_NAME: str = Field(
        default=os.getenv("GITHUB_REPO_NAME", ""),
        description="GitHub Repository Name"
    )
    GITHUB_REPO_OWNER: str = Field(
        default=os.getenv("GITHUB_REPO_OWNER", ""),
        description="GitHub Repository Owner"
    )
    TAVILY_API_KEY: str = Field(
        default=os.getenv("TAVILY_API_KEY", ""),
        description="Tavily API Key"
    )
    AGENTOPS_API_KEY: str = Field(
        default=os.getenv("AGENTOPS_API_KEY", ""),
        description="AgentOps API Key"
    )
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()