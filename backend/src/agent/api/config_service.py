"""Service layer for admin API to perform config CRUD operations.

This module provides async helper functions used by admin API routes to
perform CRUD operations against the configuration tables. Functions in this
module are thin wrappers around the ORM models exposed from
`agent.services.config_store` and take care of ensuring the backing DB is
initialized, performing the transaction, and then refreshing the in-memory
configuration cache by calling ``ConfigStore.reload()``.

Design notes:
- All functions ensure ``config_store.store.init_db()`` is called before use.
- DB sessions are created via ``config_store.store._Session()`` and used with
    ``async with`` to scope transactions.
- After mutating operations, ``config_store.store.reload()`` is awaited so the
    runtime in-memory cache and any registered post-reload hooks (for example
    workflow rebuilds) can pick up changes.

Functions in this module generally raise ``KeyError`` when an expected DB row
is not found for update/delete operations. Caller routes should translate
these to appropriate HTTP responses.
"""
from __future__ import annotations

from typing import Any, Dict, List

from sqlalchemy import select

from ..services import config_store


async def enable_segmentor(name: str) -> None:
    """Ensure a segmentor exists and mark it enabled.

    If a ``SegmentorConfig`` row for ``segmentor_name==name`` exists it will
    be updated to ``enabled=True``. If no row exists one will be created
    with an empty metadata object. After the DB transaction this function
    triggers ``config_store.store.reload()`` so the in-memory cache and any
    dependent components see the change.

    Args:
        name: Unique segmentor name to enable.
    """
    await config_store.store.init_db()
    async with config_store.store._Session() as session:
        obj = await session.get(config_store.SegmentorConfig, name)
        if obj is None:
            obj = config_store.SegmentorConfig(segmentor_name=name, enabled=True, metadata_={})
            session.add(obj)
        else:
            obj.enabled = True
        await session.commit()
    await config_store.store.reload()


async def disable_segmentor(name: str) -> None:
    """Disable a segmentor by name.

    Mirrors :func:`enable_segmentor` but sets ``enabled=False``. A new row is
    created when missing. Reloads the in-memory config cache on completion.

    Args:
        name: Segmentor name to disable.
    """
    await config_store.store.init_db()
    async with config_store.store._Session() as session:
        obj = await session.get(config_store.SegmentorConfig, name)
        if obj is None:
            obj = config_store.SegmentorConfig(segmentor_name=name, enabled=False, metadata_={})
            session.add(obj)
        else:
            obj.enabled = False
        await session.commit()
    await config_store.store.reload()


async def list_nodes() -> Dict[str, Any]:
    """Return a mapping of configured nodes.

    Reads the ``NodeConfig`` table and returns a mapping of node name ->
    dict containing the ``enabled`` flag and the ``metadata`` JSON. This is
    primarily used by admin routes to list available node configurations.

    Returns:
        Dict[str, Any]: Mapping node name -> {"enabled": bool, "metadata": dict}
    """
    await config_store.store.init_db()
    async with config_store.store._Session() as session:
        res = await session.execute(select(config_store.NodeConfig))
        rows = res.scalars().all()
        return {r.name: {"enabled": bool(r.enabled), "metadata": getattr(r, "metadata_", {})} for r in rows}


async def upsert_node(name: str, enabled: bool | None, metadata: Dict[str, Any] | None) -> None:
    """Create or update a node configuration.

    When ``name`` does not exist a new ``NodeConfig`` row is created. When an
    existing row is found only the provided fields are updated (``enabled``
    and/or ``metadata``). After the database commit the in-memory cache is
    reloaded.

    Args:
        name: Node identifier.
        enabled: If provided, sets the node enabled/disabled state.
        metadata: Optional JSON-serializable metadata to store for the node.
    """
    await config_store.store.init_db()
    async with config_store.store._Session() as session:
        obj = await session.get(config_store.NodeConfig, name)
        if obj is None:
            obj = config_store.NodeConfig(name=name, enabled=(enabled if enabled is not None else True), metadata_=(metadata or {}))
            session.add(obj)
        else:
            if enabled is not None:
                obj.enabled = enabled
            if metadata is not None:
                obj.metadata_ = metadata
        await session.commit()
    await config_store.store.reload()


async def list_routing() -> List[Dict[str, Any]]:
    """Return routing rules from the in-memory configuration cache.

    This is a read-only helper that returns the list of routing rule dicts
    currently loaded into the in-memory cache.
    """
    cfg = config_store.store.get_all_configs()
    return cfg.get("routing_rules", [])


async def add_routing(source_node: str, condition: Dict[str, Any], target_node: str, enabled: bool = True) -> int:
    """Create a new routing rule and return its primary key.

    The ``condition`` argument should be a JSON-serializable expression
    (for example JSONLogic). After inserting the row this function refreshes
    it to obtain the generated id and then reloads the in-memory cache.
    """
    await config_store.store.init_db()
    async with config_store.store._Session() as session:
        row = config_store.RoutingRule(source_node=source_node, condition=condition, target_node=target_node, enabled=enabled, metadata_={})
        session.add(row)
        await session.commit()
        await session.refresh(row)
        rid = int(row.id)
    await config_store.store.reload()
    return rid


async def delete_routing(rule_id: int) -> None:
    """Delete a routing rule by primary key.

    Raises:
        KeyError: If the routing rule does not exist.
    """
    await config_store.store.init_db()
    async with config_store.store._Session() as session:
        row = await session.get(config_store.RoutingRule, rule_id)
        if row is None:
            raise KeyError("rule not found")
        await session.delete(row)
        await session.commit()
    await config_store.store.reload()


async def get_rag_retrieval() -> List[Dict[str, Any]]:
    """Return RAG retrieval configuration entries from cache.

    Read-only helper returning a list of retrieval config dicts.
    """
    cfg = config_store.store.get_all_configs()
    return cfg.get("rag_retrieval", [])


async def patch_rag_retrieval(cfg_id: int, updates: Dict[str, Any]) -> None:
    """Patch a RAG retrieval configuration row.

    The ``updates`` mapping is applied to the ORM object. When the key is
    ``metadata`` the model attribute name is ``metadata_`` and is handled
    accordingly. Raises ``KeyError`` if the target row does not exist.
    """
    await config_store.store.init_db()
    async with config_store.store._Session() as session:
        row = await session.get(config_store.RAGRetrievalConfig, cfg_id)
        if row is None:
            raise KeyError("retrieval config not found")
        for k, v in updates.items():
            if k == "metadata":
                setattr(row, "metadata_", v)
            else:
                setattr(row, k, v)
        await session.commit()
    await config_store.store.reload()


async def get_offers() -> List[Dict[str, Any]]:
    """Return offers configuration entries from cache.

    Read-only helper returning list of offers config dicts.
    """
    cfg = config_store.store.get_all_configs()
    return cfg.get("offers", [])


async def patch_offers(cfg_id: int, updates: Dict[str, Any]) -> None:
    """Patch an offers configuration row.

    Behavior mirrors :func:`patch_rag_retrieval` but targets the
    ``OffersConfig`` model.
    """
    await config_store.store.init_db()
    async with config_store.store._Session() as session:
        row = await session.get(config_store.OffersConfig, cfg_id)
        if row is None:
            raise KeyError("offers config not found")
        for k, v in updates.items():
            if k == "metadata":
                setattr(row, "metadata_", v)
            else:
                setattr(row, k, v)
        await session.commit()
    await config_store.store.reload()


async def get_safety() -> List[Dict[str, Any]]:
    """Return safety configuration entries from cache.

    Read-only helper returning list of safety config dicts.
    """
    cfg = config_store.store.get_all_configs()
    return cfg.get("safety", [])


async def patch_safety(cfg_id: int, updates: Dict[str, Any]) -> None:
    """Patch a safety configuration row.

    Handles special mapping for ``metadata`` -> ``metadata_`` and updates
    list-like fields such as ``banned_keywords``. Raises ``KeyError`` when
    the target row is not found.
    """
    await config_store.store.init_db()
    async with config_store.store._Session() as session:
        row = await session.get(config_store.SafetyConfig, cfg_id)
        if row is None:
            raise KeyError("safety config not found")
        for k, v in updates.items():
            if k in ("metadata", "banned_keywords"):
                setattr(row, "metadata_" if k == "metadata" else k, v)
            else:
                setattr(row, k, v)
        await session.commit()
    await config_store.store.reload()


async def get_generation() -> List[Dict[str, Any]]:
    """Return generation configuration entries from cache.

    Read-only helper returning list of generation config dicts.
    """
    cfg = config_store.store.get_all_configs()
    return cfg.get("generation", [])


async def patch_generation(cfg_id: int, updates: Dict[str, Any]) -> None:
    """Patch a generation configuration row.

    Maps external ``metadata`` key to the model attribute ``metadata_`` and
    reloads the in-memory cache after commit.
    """
    await config_store.store.init_db()
    async with config_store.store._Session() as session:
        row = await session.get(config_store.GenerationConfig, cfg_id)
        if row is None:
            raise KeyError("generation config not found")
        for k, v in updates.items():
            if k == "metadata":
                setattr(row, "metadata_", v)
            else:
                setattr(row, k, v)
        await session.commit()
    await config_store.store.reload()


async def get_delivery() -> List[Dict[str, Any]]:
    """Return delivery configuration entries from cache.

    Read-only helper returning list of delivery config dicts.
    """
    cfg = config_store.store.get_all_configs()
    return cfg.get("delivery", [])


async def patch_delivery(cfg_id: int, updates: Dict[str, Any]) -> None:
    """Patch a delivery configuration row.

    Updates the delivery config ORM object with the provided mapping. Raises
    ``KeyError`` if the target row does not exist. The in-memory cache is
    reloaded after the DB commit.
    """
    await config_store.store.init_db()
    async with config_store.store._Session() as session:
        row = await session.get(config_store.DeliveryConfig, cfg_id)
        if row is None:
            raise KeyError("delivery config not found")
        for k, v in updates.items():
            if k == "metadata":
                setattr(row, "metadata_", v)
            else:
                setattr(row, k, v)
        await session.commit()
    await config_store.store.reload()
