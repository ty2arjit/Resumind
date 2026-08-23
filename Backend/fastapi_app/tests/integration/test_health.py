"""Integration: FastAPI app wiring, routing, and centralized error handling
end-to-end via TestClient. test_health_db does not require a reachable
database — it asserts the endpoint always degrades to a well-formed JSON
error rather than hanging or crashing, which is the contract regardless of
whether Postgres happens to be reachable from wherever tests run.
"""


def test_health_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_db_returns_well_formed_response(client):
    response = client.get("/health/db")
    assert response.status_code in (200, 500, 503)
    body = response.json()
    if response.status_code == 200:
        assert body == {"status": "ok"}
    else:
        assert "error" in body


def test_legacy_analyze_route_still_mounted(client):
    """The old Gemini endpoint (dev fallback, architecture decision 4) must
    still exist — Phase 1 must not remove it."""
    response = client.post("/analyze")
    # Missing required multipart fields -> 422, not 404: proves the route
    # is still registered rather than silently dropped.
    assert response.status_code == 422
