"""Unit Tests for NetAtlas Cleaner and Validator Modules."""

import pytest
import pandas as pd
from backend.preprocessing.cleaner import DataCleaner
from backend.preprocessing.validator import DataValidator
from backend.ingestion.geojson_loader import validate_wgs84_coordinates, validate_and_clean_geometry

def test_clean_string():
    assert DataCleaner.clean_string("  London  ") == "London"
    assert DataCleaner.clean_string(None) == ""
    assert DataCleaner.clean_string("NULL") == ""
    assert DataCleaner.clean_string("undefined") == ""
    assert DataCleaner.clean_string("N/A") == ""

def test_clean_coordinates():
    # Valid coordinates
    lat, lon, is_valid = DataCleaner.clean_coordinates(51.5074, -0.1278)
    assert is_valid is True
    assert lat == 51.5074
    assert lon == -0.1278

    # Null Island (0.0, 0.0) should be identified as invalid coordinate
    _, _, is_valid_null_island = DataCleaner.clean_coordinates(0.0, 0.0)
    assert is_valid_null_island is False

    # Out of range coordinates
    _, _, is_valid_out_range = DataCleaner.clean_coordinates(95.0, 200.0)
    assert is_valid_out_range is False

    # None coordinates
    _, _, is_valid_none = DataCleaner.clean_coordinates(None, None)
    assert is_valid_none is False

def test_wgs84_coordinate_bounds():
    assert validate_wgs84_coordinates(0.0, 0.0) is True
    assert validate_wgs84_coordinates(180.0, 90.0) is True
    assert validate_wgs84_coordinates(-180.0, -90.0) is True
    assert validate_wgs84_coordinates(180.1, 45.0) is False
    assert validate_wgs84_coordinates(10.0, -90.5) is False
    assert validate_wgs84_coordinates(None, 45.0) is False

def test_validate_and_clean_geometry():
    # Valid LineString
    valid_line = {
        "type": "LineString",
        "coordinates": [[10.0, 20.0], [15.0, 25.0]]
    }
    geom, err = validate_and_clean_geometry(valid_line)
    assert err is None
    assert geom is not None
    assert geom["type"] == "LineString"

    # Coordinates out of WGS84 bounds
    invalid_line = {
        "type": "LineString",
        "coordinates": [[300.0, 20.0], [15.0, 25.0]]
    }
    geom_inv, err_inv = validate_and_clean_geometry(invalid_line)
    assert geom_inv is None
    assert "bounds" in err_inv

def test_data_validator_spatial_points():
    df = pd.DataFrame({
        "latitude": [10.0, 20.0, None, 0.0, 95.0],
        "longitude": [10.0, 20.0, 30.0, 0.0, 45.0]
    })
    res = DataValidator.validate_spatial_points(df)
    assert res["total_records"] == 5
    assert res["valid_coordinates"] == 2
    assert res["invalid_or_missing_coordinates"] == 3

