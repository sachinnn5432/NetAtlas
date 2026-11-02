"""Security Standards and Control Verification Tests for NetAtlas."""

import pytest
from backend.api.app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_security_http_headers(client):
    res = client.get("/api/v1/overview")
    headers = res.headers

    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-Frame-Options") == "SAMEORIGIN"
    assert "Content-Security-Policy" in headers
    assert "Referrer-Policy" in headers

def test_sql_injection_defense(client):
    # Attempt SQL injection payload in search query
    sql_payload = "Ashburn' OR '1'='1' --"
    res = client.get(f"/api/v1/facilities?search={sql_payload}")
    assert res.status_code == 200
    # Response should be a safe JSON array, not leaking database internal dump
    data = res.get_json()
    assert isinstance(data["data"], list)

    # Attempt in country parameter
    sql_country = "US' UNION SELECT null, null, null --"
    res_country = client.get(f"/api/v1/ixps?country={sql_country}")
    assert res_country.status_code == 200
    data_country = res_country.get_json()
    assert len(data_country["data"]) == 0

def test_no_secrets_exposed_in_overview(client):
    res = client.get("/api/v1/overview")
    text = res.get_data(as_text=True)
    assert "password" not in text.lower()
    assert "secret" not in text.lower()
    assert "token" not in text.lower()

