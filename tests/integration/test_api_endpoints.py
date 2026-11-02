"""Integration Tests for NetAtlas REST API Service."""

import pytest
from backend.api.app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_overview_endpoint(client):
    res = client.get("/api/v1/overview")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    overview = data["data"]
    assert overview["total_submarine_cables"] > 0
    assert overview["total_landing_stations"] > 0
    assert overview["total_ixps"] > 0
    assert overview["total_facilities"] > 0

def test_cables_list_and_detail(client):
    res = client.get("/api/v1/cables?limit=10")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert len(data["data"]) == 10

    # Test single cable detail
    first_cable_id = data["data"][0]["id"]
    res_single = client.get(f"/api/v1/cables/{first_cable_id}")
    assert res_single.status_code == 200
    single_data = res_single.get_json()
    assert single_data["data"]["id"] == first_cable_id

    # Test 404 for non-existent cable
    res_404 = client.get("/api/v1/cables/non-existent-cable-id-xyz")
    assert res_404.status_code == 404

def test_landing_stations_endpoint(client):
    res = client.get("/api/v1/landing-stations?limit=15")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert len(data["data"]) == 15

def test_ixps_endpoint_and_filter(client):
    res = client.get("/api/v1/ixps?limit=20")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"

    # Filter by country
    res_filtered = client.get("/api/v1/ixps?country=US&limit=10")
    assert res_filtered.status_code == 200
    filtered_data = res_filtered.get_json()
    for ix in filtered_data["data"]:
        assert ix["country"] == "US"

def test_facilities_endpoint(client):
    res = client.get("/api/v1/facilities?limit=10")
    assert res.status_code == 200
    data = res.get_json()
    assert len(data["data"]) == 10

def test_global_search_endpoint(client):
    res = client.get("/api/v1/search?q=London")
    assert res.status_code == 200
    data = res.get_json()
    assert "ixps" in data["data"] or "facilities" in data["data"]

def test_analytics_endpoints(client):
    res_countries = client.get("/api/v1/analytics/countries")
    assert res_countries.status_code == 200
    assert len(res_countries.get_json()["data"]) > 0

    res_regions = client.get("/api/v1/analytics/regions")
    assert res_regions.status_code == 200
    assert len(res_regions.get_json()["data"]) > 0

    res_topo = client.get("/api/v1/analytics/network-topology")
    assert res_topo.status_code == 200
    assert "topology" in res_topo.get_json()

    res_stories = client.get("/api/v1/analytics/stories")
    assert res_stories.status_code == 200
    assert len(res_stories.get_json()["data"]) > 0

def test_geojson_endpoints(client):
    res_cables = client.get("/api/v1/geojson/cables")
    assert res_cables.status_code == 200
    assert res_cables.mimetype == "application/geo+json"

    res_landings = client.get("/api/v1/geojson/landing-stations")
    assert res_landings.status_code == 200
    assert res_landings.mimetype == "application/geo+json"

    # Invalid layer
    res_invalid = client.get("/api/v1/geojson/invalid-layer-name")
    assert res_invalid.status_code == 400

