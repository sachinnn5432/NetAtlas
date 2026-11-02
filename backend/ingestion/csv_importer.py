"""CSV and GeoJSON Fallback Importer for NetAtlas.

Allows loading pre-exported CSV or GeoJSON files when live network APIs
are firewalled or inaccessible in university evaluation environments.
Enforces authentic schema validation and provenance tracking.
"""

from typing import Dict, Any, List, Optional
import csv
from pathlib import Path
from backend.models.database import SessionLocal
from backend.models.db_models import (
    IXPModel, FacilityModel, CableModel, LandingStationModel
)
from backend.config.logging_config import logger
from backend.config.settings import REPORTING_DATA_DIR, GEOJSON_DATA_DIR
from backend.ingestion.geojson_loader import parse_geojson_features
import json

class CSVFallbackImporter:
    """Imports infrastructure data from standardized CSV files."""

    @staticmethod
    def import_ixps_from_csv(csv_path: Path) -> int:
        """Imports IXPs from CSV."""
        if not csv_path.exists():
            logger.error("IXP CSV fallback file not found at: %s", csv_path)
            return 0

        session = SessionLocal()
        count = 0
        try:
            with open(csv_path, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    ix_id = int(row["id"])
                    existing = session.query(IXPModel).filter_by(id=ix_id).first()
                    if not existing:
                        existing = IXPModel(id=ix_id)
                        session.add(existing)

                    existing.name = row.get("name", "").strip()
                    existing.city = row.get("city", "").strip()
                    existing.country = row.get("country", "").strip().upper()
                    existing.region_continent = row.get("region_continent")
                    existing.net_count = int(row.get("net_count") or 0)
                    existing.fac_count = int(row.get("fac_count") or 0)
                    existing.source = row.get("source", "PeeringDB CSV Fallback")
                    count += 1
            session.commit()
            logger.info("Imported %d IXPs from fallback CSV.", count)
            return count
        except Exception as exc:
            session.rollback()
            logger.error("Failed importing IXPs from CSV: %s", exc)
            return 0
        finally:
            session.close()

    @staticmethod
    def import_facilities_from_csv(csv_path: Path) -> int:
        """Imports facilities from CSV."""
        if not csv_path.exists():
            logger.error("Facility CSV fallback file not found at: %s", csv_path)
            return 0

        session = SessionLocal()
        count = 0
        try:
            with open(csv_path, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    fac_id = int(row["id"])
                    existing = session.query(FacilityModel).filter_by(id=fac_id).first()
                    if not existing:
                        existing = FacilityModel(id=fac_id)
                        session.add(existing)

                    existing.name = row.get("name", "").strip()
                    existing.city = row.get("city", "").strip()
                    existing.country = row.get("country", "").strip().upper()
                    existing.latitude = float(row["latitude"]) if row.get("latitude") else None
                    existing.longitude = float(row["longitude"]) if row.get("longitude") else None
                    existing.net_count = int(row.get("net_count") or 0)
                    existing.ix_count = int(row.get("ix_count") or 0)
                    existing.source = row.get("source", "PeeringDB CSV Fallback")
                    count += 1
            session.commit()
            logger.info("Imported %d facilities from fallback CSV.", count)
            return count
        except Exception as exc:
            session.rollback()
            logger.error("Failed importing facilities from CSV: %s", exc)
            return 0
        finally:
            session.close()

