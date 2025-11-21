"""Service layer for admin API to perform config CRUD operations.

These functions wrap DB access via `agent.services.config_store` and are
intended to keep routing handlers thin and testable.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from sqlalchemy import select

from ..services import config_store


async def enable_segmentor(name: str) -> None:
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
    await config_store.store.init_db()
    async with config_store.store._Session() as session:
        res = await session.execute(select(config_store.NodeConfig))
        rows = res.scalars().all()
        return {r.name: {"enabled": bool(r.enabled), "metadata": getattr(r, "metadata_", {})} for r in rows}


async def upsert_node(name: str, enabled: Optional[bool], metadata: Optional[Dict[str, Any]]) -> None:
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
    cfg = config_store.store.get_all_configs()
    return cfg.get("routing_rules", [])


async def add_routing(source_node: str, condition: Dict[str, Any], target_node: str, enabled: bool = True) -> int:
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
    await config_store.store.init_db()
    async with config_store.store._Session() as session:
        row = await session.get(config_store.RoutingRule, rule_id)
        if row is None:
            raise KeyError("rule not found")
        await session.delete(row)
        await session.commit()
    await config_store.store.reload()


async def get_rag_retrieval() -> List[Dict[str, Any]]:
    cfg = config_store.store.get_all_configs()
    return cfg.get("rag_retrieval", [])


async def patch_rag_retrieval(cfg_id: int, updates: Dict[str, Any]) -> None:
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
    cfg = config_store.store.get_all_configs()
    return cfg.get("offers", [])


async def patch_offers(cfg_id: int, updates: Dict[str, Any]) -> None:
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
    cfg = config_store.store.get_all_configs()
    return cfg.get("safety", [])


async def patch_safety(cfg_id: int, updates: Dict[str, Any]) -> None:
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
    cfg = config_store.store.get_all_configs()
    return cfg.get("generation", [])


async def patch_generation(cfg_id: int, updates: Dict[str, Any]) -> None:
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
    cfg = config_store.store.get_all_configs()
    return cfg.get("delivery", [])


async def patch_delivery(cfg_id: int, updates: Dict[str, Any]) -> None:
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
