
def test_admin_config_crud(tmp_path, monkeypatch):
    db_path = tmp_path / "segstore2.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")

    from fastapi.testclient import TestClient

    from agent.api.app import app
    from agent.services import config_store

    client = TestClient(app)

    # Nodes: initially empty
    r = client.get("/admin/nodes")
    assert r.status_code == 200
    assert isinstance(r.json(), dict)

    # Upsert a node
    payload = {"enabled": True, "metadata": {"foo": "bar"}}
    r = client.patch("/admin/nodes/test_node", json=payload)
    assert r.status_code == 200

    # Node should appear in list
    r = client.get("/admin/nodes")
    assert r.status_code == 200
    assert "test_node" in r.json()

    # Routing: add rule
    rule = {"source_node": "seg", "condition": {"segment": "x"}, "target_node": "offers"}
    r = client.post("/admin/routing", json=rule)
    assert r.status_code == 200
    rid = r.json().get("id")
    assert isinstance(rid, int)

    # List routing contains the new rule
    r = client.get("/admin/routing")
    assert r.status_code == 200
    rules = r.json().get("routing_rules", [])
    assert any(r.get("id") == rid for r in rules)

    # Delete routing
    r = client.delete(f"/admin/routing/{rid}")
    assert r.status_code == 200

    # Retrieval/generation/etc: create a generation config row directly via session
    import asyncio

    async def create_generation():
        await config_store.store.init_db()
        async with config_store.store._Session() as session:
            g = config_store.GenerationConfig(model_name="gpt-test", temperature=0.5, max_tokens=100, system_prompt="hi", metadata_={})
            session.add(g)
            await session.commit()
            await session.refresh(g)
            return int(g.id)

    gen_id = asyncio.get_event_loop().run_until_complete(create_generation())
    # Refresh the in-memory cache so the new row is visible to the API
    asyncio.get_event_loop().run_until_complete(config_store.store.reload())

    r = client.get("/admin/generation/config")
    assert r.status_code == 200
    gens = r.json().get("generation", [])
    assert any(g.get("id") == gen_id for g in gens)

    # Patch generation
    r = client.patch(f"/admin/generation/{gen_id}", json={"temperature": 0.2})
    assert r.status_code == 200
