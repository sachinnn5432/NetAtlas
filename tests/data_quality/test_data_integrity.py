"""Data Quality and Relational Integrity Automated Test Suite for NetAtlas."""

import pytest
import pandas as pd
from pathlib import Path
from backend.models.database import SessionLocal
from backend.models.db_models import (
    CableModel, LandingStationModel, IXPModel, FacilityModel, NetworkModel, DataSourceProvenanceModel
)
from backend.config.settings import REPORTING_DATA_DIR

def test_database_table_populations():
    session = SessionLocal()
    try:
        cable_count = session.query(CableModel).count()
        lp_count = session.query(LandingStationModel).count()
        ixp_count = session.query(IXPModel).count()
        fac_count = session.query(FacilityModel).count()
        net_count = session.query(NetworkModel).count()

        assert cable_count >= 500, f"Expected at least 500 cables, got {cable_count}"
        assert lp_count >= 1500, f"Expected at least 1500 landing stations, got {lp_count}"
        assert ixp_count >= 1000, f"Expected at least 1000 IXPs, got {ixp_count}"
        assert fac_count >= 2000, f"Expected at least 2000 facilities, got {fac_count}"
        assert net_count >= 2000, f"Expected at least 2000 networks, got {net_count}"
    finally:
        session.close()

def test_landing_station_coordinates_bounds():
    session = SessionLocal()
    try:
        stations = session.query(LandingStationModel).all()
        assert len(stations) > 0
        for s in stations:
            assert -90.0 <= s.latitude <= 90.0, f"Invalid latitude: {s.latitude}"
            assert -180.0 <= s.longitude <= 180.0, f"Invalid longitude: {s.longitude}"
            # Ensure not Null Island
            assert not (abs(s.latitude) < 0.0001 and abs(s.longitude) < 0.0001)
    finally:
        session.close()

def test_reporting_csv_files_exist_and_non_empty():
    required_csvs = [
        "DimCountry.csv", "DimRegion.csv", "DimDate.csv", "DimInfrastructureType.csv",
        "DimDataSource.csv", "FactCable.csv", "FactLandingStation.csv", "FactIXP.csv",
        "FactFacility.csv", "FactNetworkRelationship.csv"
    ]
    for filename in required_csvs:
        p = REPORTING_DATA_DIR / filename
        assert p.exists(), f"Missing required Power BI CSV: {filename}"
        df = pd.read_csv(p)
        assert len(df) > 0, f"CSV {filename} is empty"

def test_provenance_registry():
    session = SessionLocal()
    try:
        provs = session.query(DataSourceProvenanceModel).all()
        assert len(provs) >= 6
        for p in provs:
            assert p.license is not None and len(p.license) > 0
            assert p.url.startswith("http")
            assert len(p.known_limitations) > 10
    finally:
        session.close()

