"""
Common and Health API schemas.
"""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(..., examples=["ok"])
    service: str = Field(..., examples=["Utthan API"])
    version: str = Field(..., examples=["1.0.0"])
    environment: str = Field(..., examples=["development"])


class DBHealthResponse(BaseModel):
    status: str = Field(..., examples=["ok"])
    database: str = Field(..., examples=["connected"])
    message: str = Field(..., examples=["Database connection active and responsive"])


class ErrorResponse(BaseModel):
    detail: str = Field(..., examples=["Resource not found"])
