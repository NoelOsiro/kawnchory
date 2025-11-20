"""API routes for admin config management."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..services import config_store

router = APIRouter()

@router.get("/health")
def health_check():
    """Health check endpoint for the admin API.

    Returns:
    -------
    dict
        A mapping containing the status and a short message indicating the API is healthy.
    """
    return {"status": "ok", "message": "Admin API is healthy."}

@router.post("/admin/reload-configs")
async def admin_reload():
    """Reload admin configuration data from the config store.

    This endpoint triggers an asynchronous reload of the configuration store and
    returns the updated configuration mapping.

    Returns:
    -------
    dict
        A mapping with keys "status" (reload status) and "configs" (the updated configs).

    Raises:
    ------
    HTTPException
        If an error occurs during reload, raises HTTPException with status 500 and
        the underlying error message.
    """
    try:
        await config_store.store.reload()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return {"status": "reloaded", "configs": config_store.store.get_configs()}


@router.get("/admin/configs")
def get_configs():
    return config_store.store.get_configs()
