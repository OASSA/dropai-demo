"""
Google Maps integration for real distance/ETA lookups.
Falls back to haversine when API key is not configured.
"""
import httpx
from typing import Optional, tuple
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class MapsService:
    BASE_URL = "https://maps.googleapis.com/maps/api"

    async def get_distance_and_duration(
        self,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float,
    ) -> tuple[Optional[float], Optional[int]]:
        """
        Returns (distance_km, duration_seconds).
        Uses Google Distance Matrix API when key is present.
        """
        if not settings.GOOGLE_MAPS_API_KEY:
            logger.debug("Google Maps API key not set — skipping live lookup")
            return None, None

        url = f"{self.BASE_URL}/distancematrix/json"
        params = {
            "origins": f"{origin_lat},{origin_lng}",
            "destinations": f"{dest_lat},{dest_lng}",
            "units": "metric",
            "key": settings.GOOGLE_MAPS_API_KEY,
        }
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(url, params=params)
                data = resp.json()
                element = data["rows"][0]["elements"][0]
                if element["status"] == "OK":
                    distance_km = element["distance"]["value"] / 1000
                    duration_sec = element["duration"]["value"]
                    return distance_km, duration_sec
        except Exception as e:
            logger.warning(f"Google Maps API error: {e}")
        return None, None

    async def geocode_address(self, address: str) -> tuple[Optional[float], Optional[float]]:
        """Convert an address to lat/lng coordinates."""
        if not settings.GOOGLE_MAPS_API_KEY:
            return None, None
        url = f"{self.BASE_URL}/geocode/json"
        params = {"address": address, "key": settings.GOOGLE_MAPS_API_KEY}
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(url, params=params)
                data = resp.json()
                if data["results"]:
                    location = data["results"][0]["geometry"]["location"]
                    return location["lat"], location["lng"]
        except Exception as e:
            logger.warning(f"Geocoding error: {e}")
        return None, None


maps_service = MapsService()
