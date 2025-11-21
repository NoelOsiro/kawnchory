import asyncio

import pytest

from agent.services import config_store


def test_jsonlogic_nested_and_exists():
    jsonlogic = pytest.importorskip("jsonlogic")

    data = {"customer": {"name": "Alice", "email": "alice@example.com"}, "segment": "intent_xyz"}

    # Nested equality
    cond = {"==": [{"var": "customer.name"}, "Alice"]}
    assert jsonlogic.jsonlogic(cond, data)

    # Existence check via inequality with null
    cond2 = {"!=": [{"var": "customer.email"}, None]}
    assert jsonlogic.jsonlogic(cond2, data)

    # Complex OR: segment contains 'intent' OR user_query exists
    cond3 = {"or": [{"in": ["intent", {"var": "segment"}]}, {"var": "user_query"}]}
    assert jsonlogic.jsonlogic(cond3, data)


@pytest.mark.asyncio
async def test_config_store_persists_json_condition(tmp_path, monkeypatch):
    db_path = tmp_path / "routing.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")

    await config_store.store.init_db()
    # insert a routing rule with a JSONLogic condition
    async with config_store.store._Session() as session:
        r = config_store.RoutingRule(source_node="segment_merge", condition={"==": [{"var": "segment"}, "vip"]}, target_node="offers", enabled=True, metadata_={})
        session.add(r)
        await session.commit()
        await session.refresh(r)
        rid = int(r.id)

    # reload the in-memory cache
    await config_store.store.reload()
    cfgs = config_store.store.get_all_configs()
    rules = cfgs.get("routing_rules", [])
    assert any(r.get("id") == rid for r in rules)
