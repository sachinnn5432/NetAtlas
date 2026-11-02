"""NetAtlas Configuration Module.

Manages application settings, path resolutions, and environment variables.
"""

from pathlib import Path
import os
from typing import List

# Base Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
REPORTING_DATA_DIR = DATA_DIR / "reporting"
GEOJSON_DATA_DIR = DATA_DIR / "geojson"
LOGS_DIR = PROJECT_ROOT / "logs"
POWERBI_DIR = PROJECT_ROOT / "powerbi"

# Ensure all critical directories exist
for p in [RAW_DATA_DIR, PROCESSED_DATA_DIR, REPORTING_DATA_DIR, GEOJSON_DATA_DIR, LOGS_DIR]:
    p.mkdir(parents=True, exist_ok=True)

# Database
DB_PATH = DATA_DIR / "netatlas.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")

# Server configuration
NETATLAS_HOST = os.getenv("NETATLAS_HOST", "127.0.0.1")
NETATLAS_PORT = int(os.getenv("NETATLAS_PORT", "5000"))
NETATLAS_DEBUG = os.getenv("NETATLAS_DEBUG", "False").lower() in ("true", "1", "yes")

# Data Source URLs
PEERINGDB_API_BASE = os.getenv("PEERINGDB_API_BASE", "https://www.peeringdb.com/api")
CABLE_GEOJSON_URL = os.getenv(
    "CABLE_GEOJSON_URL",
    "https://www.submarinecablemap.com/api/v3/cable/cable-geo.json"
)
LANDING_POINT_GEOJSON_URL = os.getenv(
    "LANDING_POINT_GEOJSON_URL",
    "https://www.submarinecablemap.com/api/v3/landing-point/landing-point-geo.json"
)
CABLE_ALL_URL = os.getenv(
    "CABLE_ALL_URL",
    "https://www.submarinecablemap.com/api/v3/cable/all.json"
)
CABLE_DETAIL_BASE_URL = os.getenv(
    "CABLE_DETAIL_BASE_URL",
    "https://www.submarinecablemap.com/api/v3/cable"
)

# Ingestion & Network
REQUEST_TIMEOUT_SEC = int(os.getenv("REQUEST_TIMEOUT_SEC", "30"))
PEERINGDB_RATE_LIMIT_DELAY_SEC = float(os.getenv("PEERINGDB_RATE_LIMIT_DELAY_SEC", "0.5"))
USER_AGENT = "NetAtlas-Intelligence-Engine/1.0 (Educational Research & MCA Project Evaluation)"

# Security & CORS
ALLOWED_ORIGINS: List[str] = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5000,http://127.0.0.1:5000,http://localhost:3000"
).split(",")

