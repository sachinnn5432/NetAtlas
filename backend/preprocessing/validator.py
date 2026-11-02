"""Data Validation and Anomaly Detection Engine for NetAtlas."""

from typing import Dict, Any, List
import pandas as pd
from backend.models.database import SessionLocal
from backend.models.db_models import (
    CableModel, LandingStationModel, IXPModel, FacilityModel, NetworkModel, NetworkIXRelationshipModel
)
from backend.config.logging_config import logger

class DataValidator:
    """Validates relational integrity, ranges, outliers, and schema compliance."""

    @staticmethod
    def validate_cable_attributes(df: pd.DataFrame) -> Dict[str, Any]:
        """Validates submarine cables."""
        results = {
            "total_records": len(df),
            "missing_rfs_year": int(df["rfs_year"].isna().sum()) if "rfs_year" in df else 0,
            "missing_length": int(df["length_km"].isna().sum()) if "length_km" in df else 0,
            "outlier_years": 0,
            "outlier_lengths": 0
        }
        if "rfs_year" in df:
            valid_years = df["rfs_year"].dropna()
            results["outlier_years"] = int(((valid_years < 1950) | (valid_years > 2035)).sum())
        if "length_km" in df:
            valid_lengths = df["length_km"].dropna()
            # Cable lengths > 50,000 km (longer than Earth circumference) or negative
            results["outlier_lengths"] = int(((valid_lengths < 0) | (valid_lengths > 50000)).sum())
        return results

    @staticmethod
    def validate_spatial_points(df: pd.DataFrame, lat_col: str = "latitude", lon_col: str = "longitude") -> Dict[str, Any]:
        """Validates point coordinates."""
        total = len(df)
        if lat_col not in df or lon_col not in df:
            return {"total": total, "valid_coords": 0, "missing_coords": total}

        valid_mask = (
            df[lat_col].notna() &
            df[lon_col].notna() &
            (df[lat_col] >= -90.0) & (df[lat_col] <= 90.0) &
            (df[lon_col] >= -180.0) & (df[lon_col] <= 180.0) &
            ~((df[lat_col].abs() < 0.0001) & (df[lon_col].abs() < 0.0001))
        )
        return {
            "total_records": total,
            "valid_coordinates": int(valid_mask.sum()),
            "invalid_or_missing_coordinates": int((~valid_mask).sum()),
            "coordinate_completeness_pct": round(float(valid_mask.sum() / max(total, 1) * 100), 2)
        }

