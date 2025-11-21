import os


def test_admin_endpoints(tmp_path, monkeypatch):
    # Use a temporary file-based sqlite DB so the async engine can create tables
    db_path = tmp_path / "segstore.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")

    # Import app after setting DATABASE_URL so the ConfigStore picks the test DB
    from fastapi.testclient import TestClient

    from agent.api.app import app

    client = TestClient(app)

    # Health
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"

    # Initially configs should be a dict (may be empty)
    r = client.get("/admin/configs")
    assert r.status_code == 200
    assert isinstance(r.json(), dict)

    # Enable a segmentor
    r = client.post("/admin/segmentors/behavior_seg/enable")
    assert r.status_code == 200
    assert r.json().get("status") == "enabled"

    # Reload configs endpoint should reflect the enabled segmentor
    r = client.get("/admin/configs")
    assert r.status_code == 200
    configs = r.json()
    assert "behavior_seg" in configs and configs["behavior_seg"]["enabled"] is True

    # Disable the segmentor
    r = client.post("/admin/segmentors/behavior_seg/disable")
    assert r.status_code == 200
    assert r.json().get("status") == "disabled"

    r = client.get("/admin/configs")
    configs = r.json()
    assert configs["behavior_seg"]["enabled"] is False

    # Trigger workflow rebuild and check status
    r = client.post("/admin/workflow/reload")
    assert r.status_code == 200

    r = client.get("/admin/workflow/status")
    assert r.status_code == 200
    assert "initialized" in r.json()
