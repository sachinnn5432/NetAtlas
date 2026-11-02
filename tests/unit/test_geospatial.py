"""Unit Tests for NetAtlas Geospatial and Spatial Indexing Modules."""

import pytest
from backend.geospatial.spatial_index import haversine_distance_km, SpatialBBox
from backend.geospatial.boundary_matcher import BoundaryMatcher

def test_haversine_distance():
    # London (51.5074, -0.1278) to Paris (48.8566, 2.3522) ~ 343 km
    dist = haversine_distance_km(51.5074, -0.1278, 48.8566, 2.3522)
    assert 340.0 <= dist <= 350.0

    # Distance to self should be 0.0
    dist_zero = haversine_distance_km(10.0, 10.0, 10.0, 10.0)
    assert dist_zero == 0.0

def test_spatial_bbox():
    # Europe approx bounding box [-15, 35, 30, 65]
    bbox = SpatialBBox(min_lon=-15.0, min_lat=35.0, max_lon=30.0, max_lat=65.0)

    # London inside
    assert bbox.contains_point(-0.1278, 51.5074) is True
    # Tokyo outside
    assert bbox.contains_point(139.6917, 35.6895) is False
    # None coordinates
    assert bbox.contains_point(None, None) is False

def test_spatial_bbox_parsing():
    bbox = SpatialBBox.from_string("-10,30,40,60")
    assert bbox is not None
    assert bbox.min_lon == -10.0
    assert bbox.min_lat == 30.0
    assert bbox.max_lon == 40.0
    assert bbox.max_lat == 60.0

    assert SpatialBBox.from_string("invalid,bbox") is None

def test_boundary_matcher_regions():
    assert BoundaryMatcher.get_region_for_country("US") == "North America"
    assert BoundaryMatcher.get_region_for_country("IN") == "Asia"
    assert BoundaryMatcher.get_region_for_country("GB") == "Europe"
    assert BoundaryMatcher.get_region_for_country("BR") == "South America"
    assert BoundaryMatcher.get_region_for_country("ZA") == "Africa"
    assert BoundaryMatcher.get_region_for_country("") == "Other"

