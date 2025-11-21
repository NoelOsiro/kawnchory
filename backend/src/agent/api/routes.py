"""API routes for admin config management."""
from __future__ import annotations

import importlib
import logging
from typing import Any

from fastapi import APIRouter, HTTPException

from ..services import config_store
from . import config_service, schemas

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
def health() -> dict:
    """Return simple health check for the admin API."""
    return {"status": "ok"}


@router.post("/admin/reload-configs")
async def admin_reload() -> dict[str, Any]:
    """Reload configs from DB and (indirectly) trigger workflow rebuild."""
    try:
        await config_store.store.reload()
    except Exception as exc:
        logger.exception("Failed to reload configs")
        raise HTTPException(status_code=500, detail=str(exc))
    return {"status": "reloaded", "configs": config_store.store.get_configs()}


@router.get("/admin/configs")
def get_configs() -> dict:
    """Return the current admin configuration dictionary.

    Retrieves the in-memory cached configurations from the config store and
    returns them as a mapping of configuration names to their settings.

    Returns:
    -------
    dict
        A dictionary containing configuration objects loaded in the store.

    Raises:
    ------
    Exception
        Propagates exceptions from config_store.store.get_configs() if retrieval fails.
    """
    return config_store.store.get_configs()


@router.post("/admin/segmentors/{name}/enable")
async def enable_segmentor(name: str) -> dict[str, Any]:
    """Enable a specific segmentor by name (create row if missing)."""
    await config_service.enable_segmentor(name)
    return {"status": "enabled", "segmentor": name}


@router.post("/admin/segmentors/{name}/disable")
async def disable_segmentor(name: str) -> dict[str, Any]:
    """Disable a specific segmentor by name (create row if missing)."""
    await config_service.disable_segmentor(name)
    return {"status": "disabled", "segmentor": name}



# ----- Node endpoints -----


@router.get("/admin/nodes")
async def list_nodes() -> dict[str, Any]:
    """Return all node configs from the DB."""
    return await config_service.list_nodes()


@router.patch("/admin/nodes/{name}")
async def update_node(name: str, payload: schemas.NodeUpdateIn) -> dict[str, Any]:
    """Create or update a node config row and reload configs."""
    await config_service.upsert_node(name, payload.enabled, payload.metadata)
    return {"status": "ok", "node": name}


# ----- Routing endpoints -----


@router.get("/admin/routing")
async def list_routing() -> dict[str, Any]:
    """Return routing rules from the in-memory cache."""
    rules = await config_service.list_routing()
    return {"routing_rules": rules}


@router.post("/admin/routing")
async def add_routing(rule: schemas.RoutingRuleIn) -> dict[str, Any]:
    """Insert a new routing rule row and reload configs."""
    rid = await config_service.add_routing(rule.source_node, rule.condition, rule.target_node, bool(rule.enabled))
    return {"status": "created", "id": rid}


@router.delete("/admin/routing/{rule_id}")
async def delete_routing(rule_id: int) -> dict[str, Any]:
    """Delete a routing rule row by id and reload configs."""
    try:
        await config_service.delete_routing(rule_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="rule not found")
    return {"status": "deleted", "id": rule_id}


# ----- RAG, Offers, Safety, Generation, Delivery endpoints (list + patch by id) -----

def _find_by_id(list_, id_):
    for item in list_:
        if item.get("id") == id_:
            return item
    return None


@router.get("/admin/retrieval/config")
async def get_retrieval() -> dict[str, Any]:
    """Return RAG retrieval configuration rows from the cache."""
    rows = await config_service.get_rag_retrieval()
    return {"rag_retrieval": rows}


@router.patch("/admin/retrieval/{cfg_id}")
async def patch_retrieval(cfg_id: int, payload: schemas.RAGUpdateIn) -> dict[str, Any]:
    """Patch a RAG retrieval config row by id and reload configs."""
    try:
        await config_service.patch_rag_retrieval(cfg_id, payload.model_dump(exclude_unset=True))
    except KeyError:
        raise HTTPException(status_code=404, detail="retrieval config not found")
    return {"status": "updated", "id": cfg_id}


@router.get("/admin/offers/config")
async def get_offers() -> dict[str, Any]:
    """Return offers configuration rows from the cache."""
    rows = await config_service.get_offers()
    return {"offers": rows}


@router.patch("/admin/offers/{cfg_id}")
async def patch_offers(cfg_id: int, payload: schemas.OffersUpdateIn) -> dict[str, Any]:
    """Patch an offers config row by id and reload configs."""
    try:
        await config_service.patch_offers(cfg_id, payload.model_dump(exclude_unset=True))
    except KeyError:
        raise HTTPException(status_code=404, detail="offers config not found")
    return {"status": "updated", "id": cfg_id}


@router.get("/admin/safety")
async def get_safety() -> dict[str, Any]:
    """Return safety configuration rows from the cache."""
    rows = await config_service.get_safety()
    return {"safety": rows}


@router.patch("/admin/safety/{cfg_id}")
async def patch_safety(cfg_id: int, payload: schemas.SafetyUpdateIn) -> dict[str, Any]:
    """Patch a safety config row by id and reload configs."""
    try:
        await config_service.patch_safety(cfg_id, payload.model_dump(exclude_unset=True))
    except KeyError:
        raise HTTPException(status_code=404, detail="safety config not found")
    return {"status": "updated", "id": cfg_id}


@router.get("/admin/generation/config")
async def get_generation() -> dict[str, Any]:
    """Return generation configuration rows from the cache."""
    rows = await config_service.get_generation()
    return {"generation": rows}


@router.patch("/admin/generation/{cfg_id}")
async def patch_generation(cfg_id: int, payload: schemas.GenerationUpdateIn) -> dict[str, Any]:
    """Patch a generation config row by id and reload configs."""
    try:
        await config_service.patch_generation(cfg_id, payload.model_dump(exclude_unset=True))
    except KeyError:
        raise HTTPException(status_code=404, detail="generation config not found")
    return {"status": "updated", "id": cfg_id}


@router.get("/admin/delivery")
async def get_delivery() -> dict[str, Any]:
    """Return delivery configuration rows from the cache."""
    rows = await config_service.get_delivery()
    return {"delivery": rows}


@router.patch("/admin/delivery/{cfg_id}")
async def patch_delivery(cfg_id: int, payload: schemas.DeliveryUpdateIn) -> dict[str, Any]:
    """Patch a delivery config row by id and reload configs."""
    try:
        await config_service.patch_delivery(cfg_id, payload.model_dump(exclude_unset=True))
    except KeyError:
        raise HTTPException(status_code=404, detail="delivery config not found")
    return {"status": "updated", "id": cfg_id}


@router.post("/admin/workflow/reload")
async def admin_reload_workflow() -> dict[str, Any]:
    """Force a rebuild of the LangGraph workflow from current configs."""
    try:
        await config_store.rebuild_workflow_from_store(config_store.store.get_configs())
    except Exception as exc:
        logger.exception("Failed to rebuild workflow")
        raise HTTPException(status_code=500, detail=str(exc))
    return {"status": "workflow_rebuilt"}


@router.get("/admin/workflow/status")
async def admin_workflow_status() -> dict[str, Any]:
    """Return basic status/metadata about the currently loaded workflow."""
    try:
        wf_mod = None
        for candidate in ("agent.graph.workflow_graph", "backend.src.agent.graph.workflow_graph", "src.agent.graph.workflow_graph"):
            try:
                wf_mod = importlib.import_module(candidate)
                break
            except Exception:
                continue
        if wf_mod is None:
            raise RuntimeError("workflow_graph module not importable")

        if hasattr(wf_mod, "get_workflow"):
            wf = wf_mod.get_workflow()
        else:
            wf = getattr(wf_mod, "workflow", None)

        if wf is None:
            return {"initialized": False}

        return {"initialized": True, "workflow_type": str(type(wf))}
    except Exception as exc:
        logger.exception("Failed to read workflow status")
        raise HTTPException(status_code=500, detail=str(exc))