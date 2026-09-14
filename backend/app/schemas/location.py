"""
Location Master Schemas (States & Districts).
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class DistrictResponse(BaseModel):
    id: str = Field(..., examples=["dist-up-varanasi"])
    name: str = Field(..., examples=["Varanasi"])
    code: Optional[str] = Field(None, examples=["UP-VAR"])
    state_id: str = Field(..., examples=["state-up"])
    lgd_district_code: Optional[int] = Field(None, examples=[178])


class StateResponse(BaseModel):
    id: str = Field(..., examples=["state-up"])
    code: str = Field(..., examples=["UP"])
    name: str = Field(..., examples=["Uttar Pradesh"])
    type: str = Field(..., examples=["state"])
    lgd_code: Optional[int] = Field(None, examples=[9])


class StateDistrictsResponse(BaseModel):
    state: StateResponse
    total_districts: int = Field(..., examples=[75])
    districts: List[DistrictResponse]
