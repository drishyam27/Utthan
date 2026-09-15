"""Provider-backed coordinate resolution with strict LGD validation."""

from __future__ import annotations

import logging
import re
import unicodedata
from dataclasses import dataclass
from typing import Any, Protocol

import httpx
from supabase import Client

from app.core.config import settings
from app.schemas.location import DistrictResponse, StateResponse

logger = logging.getLogger(__name__)


class LocationProviderError(Exception):
    """The configured reverse-geocoding provider could not answer safely."""


class LocationResolutionError(Exception):
    """The provider response could not be mapped to the LGD master."""


class AmbiguousLocationError(LocationResolutionError):
    """The provider response matched more than one canonical record."""


@dataclass(frozen=True)
class ReverseGeocodeResult:
    country_code: str | None
    state_name: str | None
    district_names: tuple[str, ...]


class ReverseGeocoder(Protocol):
    def reverse(self, latitude: float, longitude: float) -> ReverseGeocodeResult:
        ...


class NominatimReverseGeocoder:
    """Development-compatible provider adapter; coordinates are never logged."""

    def __init__(self, url: str, user_agent: str, timeout_seconds: float):
        self.url = url
        self.user_agent = user_agent
        self.timeout_seconds = timeout_seconds

    def reverse(self, latitude: float, longitude: float) -> ReverseGeocodeResult:
        try:
            with httpx.Client(timeout=self.timeout_seconds) as http_client:
                response = http_client.get(
                    self.url,
                    params={
                        "lat": latitude,
                        "lon": longitude,
                        "format": "jsonv2",
                        "addressdetails": 1,
                        "zoom": 10,
                    },
                    headers={"User-Agent": self.user_agent},
                )
                response.raise_for_status()
                payload = response.json()
        except (httpx.HTTPError, ValueError, TypeError):
            logger.exception("Reverse-geocoding provider request failed")
            raise LocationProviderError from None

        address = payload.get("address") if isinstance(payload, dict) else None
        if not isinstance(address, dict):
            raise LocationProviderError

        district_fields = (
            "state_district",
            "district",
            "county",
            "city_district",
        )
        district_names = tuple(
            dict.fromkeys(
                str(address[field]).strip()
                for field in district_fields
                if address.get(field)
            )
        )
        return ReverseGeocodeResult(
            country_code=str(address.get("country_code", "")).lower() or None,
            state_name=str(address.get("state", "")).strip() or None,
            district_names=district_names,
        )


class UnavailableReverseGeocoder:
    def reverse(self, latitude: float, longitude: float) -> ReverseGeocodeResult:
        raise LocationProviderError


def get_reverse_geocoder() -> ReverseGeocoder:
    if settings.LOCATION_PROVIDER != "nominatim":
        return UnavailableReverseGeocoder()
    return NominatimReverseGeocoder(
        url=settings.LOCATION_REVERSE_GEOCODER_URL,
        user_agent=settings.LOCATION_PROVIDER_USER_AGENT,
        timeout_seconds=settings.LOCATION_PROVIDER_TIMEOUT_SECONDS,
    )


def _canonical_text(value: Any) -> str:
    normalized = unicodedata.normalize("NFKC", str(value or "")).casefold()
    normalized = normalized.replace("&", " and ")
    normalized = re.sub(r"[^\w\s]", " ", normalized, flags=re.UNICODE)
    return " ".join(normalized.split())


class LocationResolver:
    """Maps provider text only to exact canonical LGD records."""

    def __init__(self, client: Client, geocoder: ReverseGeocoder):
        self.client = client
        self.geocoder = geocoder

    def resolve(self, latitude: float, longitude: float) -> dict[str, dict[str, Any]]:
        reverse_result = self.geocoder.reverse(latitude, longitude)
        if reverse_result.country_code and reverse_result.country_code != "in":
            raise LocationResolutionError

        state_res = self.client.table("states").select(
            "id, code, name, type, lgd_code"
        ).execute()
        state_rows = state_res.data or []
        state_matches = [
            row for row in state_rows
            if _canonical_text(row.get("name")) == _canonical_text(reverse_result.state_name)
        ]
        if len(state_matches) > 1:
            raise AmbiguousLocationError
        if not state_matches:
            raise LocationResolutionError
        state = StateResponse(**state_matches[0])

        district_res = self.client.table("districts").select(
            "id, name, code, state_id, lgd_district_code"
        ).eq("state_id", state.id).execute()
        district_rows = district_res.data or []
        district_matches = [
            row for row in district_rows
            if any(
                _canonical_text(row.get("name")) == _canonical_text(candidate)
                for candidate in reverse_result.district_names
            )
        ]
        if len(district_matches) > 1:
            raise AmbiguousLocationError
        if not district_matches:
            raise LocationResolutionError
        district = DistrictResponse(**district_matches[0])

        return {"state": state.model_dump(), "district": district.model_dump()}
