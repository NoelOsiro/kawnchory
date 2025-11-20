from agent.graph.nodes.hitl import hitl_node
from agent.services import hitl_queue


def test_hitl_enqueues_review(tmp_path, monkeypatch):
    # Ensure DB is created in a temp location for test isolation
    db_path = tmp_path / "hitl_test.db"
    monkeypatch.setenv("HITL_DB_PATH", str(db_path))

    state = {"safety_report": {"reasons": ["offers_sanity_failed"]}}
    out = hitl_node(state)
    assert out["status"] == "pending"
    review_id = out["review_id"]
    assert isinstance(review_id, int)

    pending = hitl_queue.list_pending()
    assert any(r["id"] == review_id for r in pending)

