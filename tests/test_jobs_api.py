import pytest
from fastapi.testclient import TestClient
from app.api.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_jobs_endpoint():
    r = client.get("/jobs", params={"country": "US", "query": "data scientist", "limit": 5})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 5
    assert len(data["items"]) == 5
    first = data["items"][0]
    assert {"title", "company", "job_url"}.issubset(first.keys())
