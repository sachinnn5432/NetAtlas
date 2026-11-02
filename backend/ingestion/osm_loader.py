"""Geographic Reference and OSM Loader.

Provides country boundary references, ISO code mapping, regional classifications,
and coordinate standardization.
"""

from typing import Dict, Any, List, Optional
import json
from pathlib import Path
from backend.models.database import SessionLocal
from backend.models.db_models import CountryReferenceModel
from backend.config.settings import RAW_DATA_DIR
from backend.config.logging_config import logger

# Comprehensive ISO 3166-1 standard dataset with coordinates and UN continental regions
CORE_COUNTRIES: List[Dict[str, Any]] = [
    {"iso2": "US", "iso3": "USA", "name": "United States", "region": "North America", "subregion": "Northern America", "lat": 37.0902, "lon": -95.7129},
    {"iso2": "IN", "iso3": "IND", "name": "India", "region": "Asia", "subregion": "Southern Asia", "lat": 20.5937, "lon": 78.9629},
    {"iso2": "GB", "iso3": "GBR", "name": "United Kingdom", "region": "Europe", "subregion": "Northern Europe", "lat": 55.3781, "lon": -3.4360},
    {"iso2": "DE", "iso3": "DEU", "name": "Germany", "region": "Europe", "subregion": "Western Europe", "lat": 51.1657, "lon": 10.4515},
    {"iso2": "FR", "iso3": "FRA", "name": "France", "region": "Europe", "subregion": "Western Europe", "lat": 46.2276, "lon": 2.2137},
    {"iso2": "NL", "iso3": "NLD", "name": "Netherlands", "region": "Europe", "subregion": "Western Europe", "lat": 52.1326, "lon": 5.2913},
    {"iso2": "SG", "iso3": "SGP", "name": "Singapore", "region": "Asia", "subregion": "South-Eastern Asia", "lat": 1.3521, "lon": 103.8198},
    {"iso2": "JP", "iso3": "JPN", "name": "Japan", "region": "Asia", "subregion": "Eastern Asia", "lat": 36.2048, "lon": 138.2529},
    {"iso2": "AU", "iso3": "AUS", "name": "Australia", "region": "Oceania", "subregion": "Australia and New Zealand", "lat": -25.2744, "lon": 133.7751},
    {"iso2": "BR", "iso3": "BRA", "name": "Brazil", "region": "South America", "subregion": "South America", "lat": -14.2350, "lon": -51.9253},
    {"iso2": "ZA", "iso3": "ZAF", "name": "South Africa", "region": "Africa", "subregion": "Southern Africa", "lat": -30.5595, "lon": 22.9375},
    {"iso2": "KE", "iso3": "KEN", "name": "Kenya", "region": "Africa", "subregion": "Eastern Africa", "lat": -0.0236, "lon": 37.9062},
    {"iso2": "NG", "iso3": "NGA", "name": "Nigeria", "region": "Africa", "subregion": "Western Africa", "lat": 9.0820, "lon": 8.6753},
    {"iso2": "EG", "iso3": "EGY", "name": "Egypt", "region": "Africa", "subregion": "Northern Africa", "lat": 26.8206, "lon": 30.8025},
    {"iso2": "AE", "iso3": "ARE", "name": "United Arab Emirates", "region": "Middle East", "subregion": "Western Asia", "lat": 23.4241, "lon": 53.8478},
    {"iso2": "CA", "iso3": "CAN", "name": "Canada", "region": "North America", "subregion": "Northern America", "lat": 56.1304, "lon": -106.3468},
    {"iso2": "MX", "iso3": "MEX", "name": "Mexico", "region": "North America", "subregion": "Central America", "lat": 23.6345, "lon": -102.5528},
    {"iso2": "ES", "iso3": "ESP", "name": "Spain", "region": "Europe", "subregion": "Southern Europe", "lat": 40.4637, "lon": -3.7492},
    {"iso2": "IT", "iso3": "ITA", "name": "Italy", "region": "Europe", "subregion": "Southern Europe", "lat": 41.8719, "lon": 12.5674},
    {"iso2": "SE", "iso3": "SWE", "name": "Sweden", "region": "Europe", "subregion": "Northern Europe", "lat": 60.1282, "lon": 18.6435},
    {"iso2": "NO", "iso3": "NOR", "name": "Norway", "region": "Europe", "subregion": "Northern Europe", "lat": 60.4720, "lon": 8.4689},
    {"iso2": "FI", "iso3": "FIN", "name": "Finland", "region": "Europe", "subregion": "Northern Europe", "lat": 61.9241, "lon": 25.7482},
    {"iso2": "CH", "iso3": "CHE", "name": "Switzerland", "region": "Europe", "subregion": "Western Europe", "lat": 46.8182, "lon": 8.2275},
    {"iso2": "IE", "iso3": "IRL", "name": "Ireland", "region": "Europe", "subregion": "Northern Europe", "lat": 53.1424, "lon": -7.6921},
    {"iso2": "HK", "iso3": "HKG", "name": "Hong Kong", "region": "Asia", "subregion": "Eastern Asia", "lat": 22.3193, "lon": 114.1694},
    {"iso2": "KR", "iso3": "KOR", "name": "South Korea", "region": "Asia", "subregion": "Eastern Asia", "lat": 35.9078, "lon": 127.7669},
    {"iso2": "CN", "iso3": "CHN", "name": "China", "region": "Asia", "subregion": "Eastern Asia", "lat": 35.8617, "lon": 104.1954},
    {"iso2": "TW", "iso3": "TWN", "name": "Taiwan", "region": "Asia", "subregion": "Eastern Asia", "lat": 23.6978, "lon": 120.9605},
    {"iso2": "ID", "iso3": "IDN", "name": "Indonesia", "region": "Asia", "subregion": "South-Eastern Asia", "lat": -0.7893, "lon": 113.9213},
    {"iso2": "MY", "iso3": "MYS", "name": "Malaysia", "region": "Asia", "subregion": "South-Eastern Asia", "lat": 4.2105, "lon": 101.9758},
    {"iso2": "TH", "iso3": "THA", "name": "Thailand", "region": "Asia", "subregion": "South-Eastern Asia", "lat": 15.8700, "lon": 100.9925},
    {"iso2": "VN", "iso3": "VNM", "name": "Vietnam", "region": "Asia", "subregion": "South-Eastern Asia", "lat": 14.0583, "lon": 108.2772},
    {"iso2": "PH", "iso3": "PHL", "name": "Philippines", "region": "Asia", "subregion": "South-Eastern Asia", "lat": 12.8797, "lon": 121.7740},
    {"iso2": "NZ", "iso3": "NZL", "name": "New Zealand", "region": "Oceania", "subregion": "Australia and New Zealand", "lat": -40.9006, "lon": 174.8860},
    {"iso2": "CL", "iso3": "CHL", "name": "Chile", "region": "South America", "subregion": "South America", "lat": -35.6751, "lon": -71.5430},
    {"iso2": "AR", "iso3": "ARG", "name": "Argentina", "region": "South America", "subregion": "South America", "lat": -38.4161, "lon": -63.6167},
    {"iso2": "CO", "iso3": "COL", "name": "Colombia", "region": "South America", "subregion": "South America", "lat": 4.5709, "lon": -74.2973},
    {"iso2": "SA", "iso3": "SAU", "name": "Saudi Arabia", "region": "Middle East", "subregion": "Western Asia", "lat": 23.8859, "lon": 45.0792},
    {"iso2": "IL", "iso3": "ISR", "name": "Israel", "region": "Middle East", "subregion": "Western Asia", "lat": 31.0461, "lon": 34.8516},
    {"iso2": "TR", "iso3": "TUR", "name": "Turkey", "region": "Middle East", "subregion": "Western Asia", "lat": 38.9637, "lon": 35.2433},
    {"iso2": "RU", "iso3": "RUS", "name": "Russia", "region": "Europe/Asia", "subregion": "Eastern Europe", "lat": 61.5240, "lon": 105.3188},
    {"iso2": "PL", "iso3": "POL", "name": "Poland", "region": "Europe", "subregion": "Eastern Europe", "lat": 51.9194, "lon": 19.1451},
    {"iso2": "CZ", "iso3": "CZE", "name": "Czech Republic", "region": "Europe", "subregion": "Eastern Europe", "lat": 49.8175, "lon": 15.4730},
    {"iso2": "AT", "iso3": "AUT", "name": "Austria", "region": "Europe", "subregion": "Western Europe", "lat": 47.5162, "lon": 14.5501},
    {"iso2": "BE", "iso3": "BEL", "name": "Belgium", "region": "Europe", "subregion": "Western Europe", "lat": 50.5039, "lon": 4.4699},
    {"iso2": "PT", "iso3": "PRT", "name": "Portugal", "region": "Europe", "subregion": "Southern Europe", "lat": 39.3999, "lon": -8.2245},
    {"iso2": "GR", "iso3": "GRC", "name": "Greece", "region": "Europe", "subregion": "Southern Europe", "lat": 39.0742, "lon": 21.8243},
    {"iso2": "DK", "iso3": "DNK", "name": "Denmark", "region": "Europe", "subregion": "Northern Europe", "lat": 56.2639, "lon": 9.5018},
    {"iso2": "GH", "iso3": "GHA", "name": "Ghana", "region": "Africa", "subregion": "Western Africa", "lat": 7.9465, "lon": -1.0232},
    {"iso2": "DJ", "iso3": "DJI", "name": "Djibouti", "region": "Africa", "subregion": "Eastern Africa", "lat": 11.8251, "lon": 42.5903},
    {"iso2": "OM", "iso3": "OMN", "name": "Oman", "region": "Middle East", "subregion": "Western Asia", "lat": 21.4735, "lon": 55.9754},
    {"iso2": "PK", "iso3": "PAK", "name": "Pakistan", "region": "Asia", "subregion": "Southern Asia", "lat": 30.3753, "lon": 69.3451},
    {"iso2": "BD", "iso3": "BGD", "name": "Bangladesh", "region": "Asia", "subregion": "Southern Asia", "lat": 23.6850, "lon": 90.3563},
    {"iso2": "LK", "iso3": "LKA", "name": "Sri Lanka", "region": "Asia", "subregion": "Southern Asia", "lat": 7.8731, "lon": 80.7718},
    {"iso2": "MA", "iso3": "MAR", "name": "Morocco", "region": "Africa", "subregion": "Northern Africa", "lat": 31.7917, "lon": -7.0926},
    {"iso2": "MU", "iso3": "MUS", "name": "Mauritius", "region": "Africa", "subregion": "Eastern Africa", "lat": -20.3484, "lon": 57.5522},
    {"iso2": "PA", "iso3": "PAN", "name": "Panama", "region": "North America", "subregion": "Central America", "lat": 8.5379, "lon": -80.7821},
    {"iso2": "CR", "iso3": "CRI", "name": "Costa Rica", "region": "North America", "subregion": "Central America", "lat": 9.7489, "lon": -83.7534},
    {"iso2": "PE", "iso3": "PER", "name": "Peru", "region": "South America", "subregion": "South America", "lat": -9.1900, "lon": -75.0152},
    {"iso2": "EC", "iso3": "ECU", "name": "Ecuador", "region": "South America", "subregion": "South America", "lat": -1.8312, "lon": -78.1834}
]

# Lookup dictionary for fast resolution
_NAME_TO_ISO2: Dict[str, str] = {c["name"].lower(): c["iso2"] for c in CORE_COUNTRIES}
_ISO2_TO_COUNTRY: Dict[str, Dict[str, Any]] = {c["iso2"]: c for c in CORE_COUNTRIES}

def populate_country_reference():
    """Populates country reference data in SQLite."""
    session = SessionLocal()
    try:
        for c in CORE_COUNTRIES:
            existing = session.query(CountryReferenceModel).filter_by(iso2=c["iso2"]).first()
            if not existing:
                ref = CountryReferenceModel(
                    iso2=c["iso2"],
                    iso3=c["iso3"],
                    country_name=c["name"],
                    region=c["region"],
                    subregion=c["subregion"],
                    latitude=c["lat"],
                    longitude=c["lon"]
                )
                session.add(ref)
        session.commit()
        logger.info("Country reference database populated with %d core economies.", len(CORE_COUNTRIES))
    except Exception as exc:
        session.rollback()
        logger.error("Error populating country reference: %s", exc)
        raise
    finally:
        session.close()

def resolve_country_code(country_name_or_code: str) -> Optional[str]:
    """Resolves an ISO2 country code from either code or full English name."""
    if not country_name_or_code:
        return None
    val = country_name_or_code.strip()
    if len(val) == 2 and val.upper() in _ISO2_TO_COUNTRY:
        return val.upper()
    return _NAME_TO_ISO2.get(val.lower())

def get_country_info(iso2: str) -> Optional[Dict[str, Any]]:
    """Gets metadata for an ISO2 country."""
    return _ISO2_TO_COUNTRY.get(iso2.upper())

