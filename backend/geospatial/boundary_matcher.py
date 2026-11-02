"""Geographic Boundary and Regional Attribution Matcher for NetAtlas."""

from typing import Dict, Any, List, Optional
from backend.models.database import SessionLocal
from backend.models.db_models import CountryReferenceModel
from backend.ingestion.osm_loader import get_country_info, resolve_country_code

class BoundaryMatcher:
    """Matches coordinates and ISO codes to regional definitions."""

    @staticmethod
    def get_region_for_country(country_code: str) -> str:
        """Returns standard UN macro-region for a country ISO2 code."""
        if not country_code:
            return "Other"
        info = get_country_info(country_code)
        if info:
            return info.get("region", "Other")

        # Fallback continent mapping
        continent_map = {
            "NA": "North America", "EU": "Europe", "AS": "Asia",
            "AF": "Africa", "OC": "Oceania", "SA": "South America"
        }
        return continent_map.get(country_code.upper(), "Global / Multi-region")

