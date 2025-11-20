import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from agent.services.config_store import (
    Base,
    ConfigStore,
    SegmentorConfig,
    rebuild_workflow_from_store,
)


@pytest.fixture()
def temp_db(tmp_path):
    db_path = tmp_path / "test_segmentors.db"
    url = f"sqlite+aiosqlite:///{db_path}"
    store = ConfigStore(database_url=url)
    # initialize DB synchronously for tests
    import asyncio

    asyncio.run(store.init_db())
    return store


def test_reload_populates_store(temp_db):
    store: ConfigStore = temp_db
    # Insert a row directly via SQLAlchemy async session
    import asyncio

    async def _insert():
        async with store._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async_session = sessionmaker(store._engine, class_=AsyncSession, expire_on_commit=False)
        async with async_session() as session:
            cfg = SegmentorConfig(segmentor_name="behavior_seg", enabled=True, metadata_={"foo": "bar"})
            session.add(cfg)
            await session.commit()

        await store.reload()

    asyncio.run(_insert())
    configs = store.get_configs()
    assert "behavior_seg" in configs
    assert configs["behavior_seg"]["enabled"] is True
    assert configs["behavior_seg"]["metadata"]["foo"] == "bar"


def test_rebuild_workflow_swaps_workflow(temp_db, monkeypatch):
    store: ConfigStore = temp_db
    # Insert two configs: behavior enabled, profile disabled
    import asyncio

    async def _insert_and_reload():
        async_session = sessionmaker(store._engine, class_=AsyncSession, expire_on_commit=False)
        async with async_session() as session:
            session.add_all([
                SegmentorConfig(segmentor_name="behavior_seg", enabled=True, metadata_={}),
                SegmentorConfig(segmentor_name="profile_seg", enabled=False, metadata_={}),
            ])
            await session.commit()
        await store.reload()

    asyncio.run(_insert_and_reload())
    # Monkeypatch the workflow_graph module used by rebuild to expose a testable API
    class DummyWF:
        def __init__(self, name):
            self.name = name

    class DummyModule:
        def __init__(self):
            self.last_created = None

        def create_workflow(self, compiled=True, enabled_segments=None, name=None):
            self.last_created = (compiled, frozenset(enabled_segments or set()), name)
            return DummyWF(self.last_created)

        def replace_workflow(self, wf):
            self.replaced = wf

    dummy = DummyModule()

    # Monkeypatch importlib to return our dummy for the agent.graph.workflow_graph name
    import importlib
    real_import_module = importlib.import_module

    def fake_import(name, package=None):
        if name == "agent.graph.workflow_graph":
            return dummy
        return real_import_module(name, package=package)

    monkeypatch.setattr(importlib, "import_module", fake_import)

    # Call rebuild
    import asyncio

    # Call rebuild with the temp store's configs so the function uses the
    # test database rather than the module-level `store`.
    asyncio.run(rebuild_workflow_from_store(configs=store.get_configs()))

    # Verify the dummy module was used and replaced workflow created
    assert isinstance(dummy.replaced, DummyWF)
    # The enabled set should only include behavior_seg
    assert dummy.last_created[1] == frozenset({"behavior_seg"})
