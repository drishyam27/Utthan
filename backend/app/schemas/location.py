"""
Location Master Schemas (States & Districts).
"""

import math
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class LocationResolveRequest(BaseModel):
    """Transient browser coordinates used only for canonical location resolution."""

    latitude: float = Field(..., ge=-90, le=90, examples=[25.3176])
    longitude: float = Field(..., ge=-180, le=180, examples=[82.9739])
    accuracy: Optional[float] = Field(None, gt=0, le=100000, examples=[35.0])

    @field_validator("latitude", "longitude", "accuracy", mode="before")
    @classmethod
    def reject_non_finite_numbers(cls, value):
        if value is not None and isinstance(value, (int, float)) and not math.isfinite(value):
            raise ValueError("coordinate values must be finite numbers")
        return value


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


class ResolvedLocationResponse(BaseModel):
    """Canonical LGD state and district returned after reverse resolution."""

    state: StateResponse
    district: DistrictResponse
