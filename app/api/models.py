"""
Pydantic Model Definition
"""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class AlertAnnotation(BaseModel):
    description: str = Field(default="No description provided")
    summary: str = Field(default="No summary provided")


class Alert(BaseModel):
    annotations: AlertAnnotation
    labels: Optional[Dict[str, str]] = None
    startsAt: Optional[str] = None
    endsAt: Optional[str] = None
    generatorURL: Optional[str] = None
    status: Optional[str] = None
    fingerprint: Optional[str] = None


class AlertRequest(BaseModel):
    alerts: List[Alert]
    commonAnnotations: Optional[Dict[str, str]] = None
    commonLabels: Optional[Dict[str, str]] = None
    externalURL: Optional[str] = None
    groupKey: Optional[str] = None
    groupLabels: Optional[Dict[str, str]] = None
    receiver: Optional[str] = None
    status: Optional[str] = None
    version: Optional[str] = None


class AnalysisResult(BaseModel):
    problem: str = Field(description="Current Problem of the Alert")
    cause: str = Field(description="Cause of the Problem")
    solution: str = Field(description="Solution to the Problem")


class AnalysisResponse(BaseModel):
    status: str
    analysis: Optional[AnalysisResult] = None
    raw_response: Optional[str] = None
    message: Optional[str] = None


class HealthCheckResponse(BaseModel):
    status: str
    timestamp: str
