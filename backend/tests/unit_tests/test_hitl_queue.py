from agent.services import hitl_queue
import os


def test_enqueue_and_approve(tmp_path, monkeypatch):
    db_path = tmp_path / "hitl_queue.db"
    monkeypatch.setenv("HITL_DB_PATH", str(db_path))

    state = {"foo": "bar"}
    rid = hitl_queue.enqueue_review(state)
    assert isinstance(rid, int)

    pending = hitl_queue.list_pending()
    assert any(p["id"] == rid for p in pending)

    # Approve the review
    ok = hitl_queue.approve_review(rid, reviewer="tester", notes="ok", result={"approved": True})
    assert ok is True

    r = hitl_queue.get_review(rid)
    assert r is not None
    assert r["status"] == "approved"
