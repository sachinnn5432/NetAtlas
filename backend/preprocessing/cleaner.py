"""Data Cleaning and Normalization Pipeline for NetAtlas."""

import pandas as pd
import numpy as np
import re
from typing import Dict, Any, List, Tuple
from backend.config.logging_config import logger
from backend.ingestion.osm_loader import resolve_country_code

class DataCleaner:
    """Provides reproducible data cleaning routines across infrastructure entities."""

    @staticmethod
    def clean_string(val: Any) -> str:
        """Trims whitespace and converts empty/placeholder values to None/empty string."""
        if val is None or pd.isna(val):
            return ""
        s = str(val).strip()
        if s.lower() in ("none", "null", "nan", "n/a", "undefined"):
            return ""
        return s

    @staticmethod
    def clean_coordinates(lat: Any, lon: Any) -> Tuple[float, float, bool]:
        """Validates and cleans geographic coordinates.

        Returns (cleaned_lat, cleaned_lon, is_valid).
        """
        try:
            if lat is None or lon is None or pd.isna(lat) or pd.isna(lon):
                return None, None, False
            c_lat = float(lat)
            c_lon = float(lon)

            # Check WGS84 range
            if not (-90.0 <= c_lat <= 90.0 and -180.0 <= c_lon <= 180.0):
                return None, None, False

            # Check for (0.0, 0.0) "Null Island" coordinates which are often default errors
            if abs(c_lat) < 0.0001 and abs(c_lon) < 0.0001:
                return None, None, False

            return round(c_lat, 6), round(c_lon, 6), True
        except (ValueError, TypeError):
            return None, None, False

    @staticmethod
    def normalize_country_code(raw_country: str) -> str:
        """Resolves ISO2 2-letter country code."""
        cleaned = DataCleaner.clean_string(raw_country)
        if not cleaned:
            return ""
        iso2 = resolve_country_code(cleaned)
        return iso2 or cleaned.upper()[:2]

    @staticmethod
    def clean_integer(val: Any, default: int = 0) -> int:
        """Converts value to integer safely."""
        try:
            if val is None or pd.isna(val):
                return default
            return int(float(val))
        except (ValueError, TypeError):
            return default

