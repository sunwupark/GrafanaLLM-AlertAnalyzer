"""
Application configuration settings.
"""
import os
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# 환경 변수 로드 (.env 파일이 있는 경우)
load_dotenv()

class Settings(BaseSettings):
    # LLM 관련 설정
    OPENAI_API_KEY: str = Field(
        default=os.getenv("OPENAI_API_KEY", ""),
        description="OpenAI API Key"
    )
    LLM_MODEL: str = Field(
        default=os.getenv("LLM_MODEL", "gpt-4o-mini"),
        description="LLM Model Name"
    )
    
    # Grafana 관련 설정
    GRAFANA_URL: str = Field(
        default=os.getenv("GRAFANA_URL", "http://localhost:3000"),
        description="Grafana API URL"
    )
    GRAFANA_API_KEY: str = Field(
        default=os.getenv("GRAFANA_API_KEY", ""),
        description="Grafana API Key"
    )
    
    # 이메일 알림 관련 설정
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
    
    # 로깅 설정
    LOG_LEVEL: str = Field(
        default=os.getenv("LOG_LEVEL", "INFO"),
        description="logging level"
    )
    
    # 추가 설정: 모델 설정 업데이트 - extra 필드 허용
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"  # 정의되지 않은 추가 필드 무시
    )


# 전역 설정 객체 생성
settings = Settings()