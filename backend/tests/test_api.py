import pytest
from app.config import get_settings


@pytest.mark.asyncio
async def test_health(client):
    ac, _ = client
    r = await ac.get("/api/v1/health")
    assert r.status_code == 200
    body = r.json()["data"]
    assert body["status"] in {"ok", "degraded"}
    assert body["database"] == "ok"


@pytest.mark.asyncio
async def test_me_citizen(client):
    ac, seed = client
    get_settings.cache_clear()
    r = await ac.get("/api/v1/me", headers={"Authorization": "Bearer x"})
    assert r.status_code == 200
    assert r.json()["data"]["role"] == "citizen"
    assert "grievance:create" in r.json()["data"]["permissions"]


@pytest.mark.asyncio
async def test_create_and_list_grievance(client):
    ac, seed = client
    payload = {
        "description": "Garbage has not been collected on our street for two weeks near Ward 5 market area.",
        "location_text": "Ward 5 market street",
        "ward_or_locality": "Ward 5",
    }
    r = await ac.post("/api/v1/grievances", json=payload, headers={"Authorization": "Bearer x"})
    assert r.status_code == 201
    ref = r.json()["data"]["reference_id"]
    assert ref.startswith("RTGS-")
    r2 = await ac.get("/api/v1/grievances", headers={"Authorization": "Bearer x"})
    assert r2.status_code == 200
    assert r2.json()["meta"]["total"] >= 1


@pytest.mark.asyncio
async def test_citizen_cannot_see_other_grievance(client, monkeypatch):
    ac, seed = client
    payload = {
        "description": "Water pipeline leak flooding the lane for several days in colony area.",
        "location_text": "Colony lane 2",
    }
    await ac.post("/api/v1/grievances", json=payload, headers={"Authorization": "Bearer x"})
    monkeypatch.setenv("AUTH_DEV_USER_ID", str(seed["other_citizen"]))
    get_settings.cache_clear()
    r = await ac.get("/api/v1/grievances", headers={"Authorization": "Bearer y"})
    assert r.status_code == 200
    assert r.json()["meta"]["total"] == 0


@pytest.mark.asyncio
async def test_analyze_endpoint(client):
    ac, seed = client
    payload = {
        "description": "Street lights not working on main road since last week, area is dark and unsafe at night.",
        "location_text": "Main road sector 4",
    }
    create = await ac.post("/api/v1/grievances", json=payload, headers={"Authorization": "Bearer x"})
    gid = create.json()["data"]["id"]
    r = await ac.post(f"/api/v1/grievances/{gid}/analyze", json={"force": True}, headers={"Authorization": "Bearer x"})
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["source"] == "rules"
    assert "confidence" in data
    assert isinstance(data["follow_up_questions"], list)


@pytest.mark.asyncio
async def test_officer_assignment_and_transition(client, monkeypatch):
    ac, seed = client
    monkeypatch.setenv("AUTH_DEV_USER_ID", str(seed["citizen_id"]))
    get_settings.cache_clear()
    payload = {
        "description": "Large pothole on highway causing accidents for the past month near bus stop.",
        "location_text": "Highway bus stop",
    }
    create = await ac.post("/api/v1/grievances", json=payload, headers={"Authorization": "Bearer x"})
    gid = create.json()["data"]["id"]
    monkeypatch.setenv("AUTH_DEV_USER_ID", str(seed["admin_id"]))
    get_settings.cache_clear()
    assign = await ac.post(
        f"/api/v1/grievances/{gid}/assignments",
        json={"department_id": str(seed["road_id"]), "officer_id": str(seed["officer_id"])},
        headers={"Authorization": "Bearer admin"},
    )
    assert assign.status_code == 201
    trans = await ac.post(
        f"/api/v1/grievances/{gid}/transitions",
        json={"to_status": "in_progress", "remark": "Inspection scheduled"},
        headers={"Authorization": "Bearer admin"},
    )
    assert trans.status_code == 200
    assert trans.json()["data"]["status"] == "in_progress"


@pytest.mark.asyncio
async def test_feedback_after_resolve(client, monkeypatch):
    ac, seed = client
    payload = {
        "description": "Drainage blocked and water stagnant for days causing mosquito problem in ward.",
        "location_text": "Ward 8 drainage point",
    }
    create = await ac.post("/api/v1/grievances", json=payload, headers={"Authorization": "Bearer x"})
    gid = create.json()["data"]["id"]
    monkeypatch.setenv("AUTH_DEV_USER_ID", str(seed["admin_id"]))
    get_settings.cache_clear()
    await ac.post(
        f"/api/v1/grievances/{gid}/assignments",
        json={"department_id": str(seed["san_id"]), "officer_id": str(seed["officer_id"])},
        headers={"Authorization": "Bearer a"},
    )
    await ac.post(
        f"/api/v1/grievances/{gid}/transitions",
        json={"to_status": "in_progress"},
        headers={"Authorization": "Bearer a"},
    )
    await ac.post(
        f"/api/v1/grievances/{gid}/transitions",
        json={"to_status": "resolved"},
        headers={"Authorization": "Bearer a"},
    )
    monkeypatch.setenv("AUTH_DEV_USER_ID", str(seed["citizen_id"]))
    get_settings.cache_clear()
    fb = await ac.post(
        f"/api/v1/grievances/{gid}/feedback",
        json={"rating": 4, "satisfaction_score": 4, "comment": "Resolved well"},
        headers={"Authorization": "Bearer c"},
    )
    assert fb.status_code == 201
    fb2 = await ac.post(
        f"/api/v1/grievances/{gid}/feedback",
        json={"rating": 5},
        headers={"Authorization": "Bearer c"},
    )
    assert fb2.status_code == 409


@pytest.mark.asyncio
async def test_notifications_list(client):
    ac, seed = client
    payload = {
        "description": "Garbage pile near park untreated for many days in residential colony area.",
        "location_text": "Park colony",
    }
    await ac.post("/api/v1/grievances", json=payload, headers={"Authorization": "Bearer x"})
    r = await ac.get("/api/v1/notifications", headers={"Authorization": "Bearer x"})
    assert r.status_code == 200
    assert len(r.json()["data"]) >= 1


@pytest.mark.asyncio
async def test_analytics_admin(client, monkeypatch):
    ac, seed = client
    monkeypatch.setenv("AUTH_DEV_USER_ID", str(seed["admin_id"]))
    get_settings.cache_clear()
    r = await ac.get("/api/v1/analytics/overview", headers={"Authorization": "Bearer admin"})
    assert r.status_code == 200
    assert "total_grievances" in r.json()["data"]
