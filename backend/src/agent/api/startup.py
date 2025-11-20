"""Startup helpers for the admin API.

This module performs DB initialization and registers the config reload
hook. Rebuild of the workflow is scheduled asynchronously to avoid
import-time circular initialization issues.
"""
from __future__ import annotations

import asyncio

from ..services import config_store


async def startup() -> None:
    # initialize DB/tables
    await config_store.store.init_db()

    # Perform initial load without invoking the reload hook to avoid
    # circular import / partial-initialization races during startup.
    config_store.store._on_reload = None
    await config_store.store.reload()

    def _schedule_rebuild(cfgs):
        return asyncio.create_task(config_store.rebuild_workflow_from_store(cfgs))

    config_store.store.register_on_reload(_schedule_rebuild)
    # Schedule an initial rebuild asynchronously so it runs after startup
    asyncio.create_task(config_store.rebuild_workflow_from_store(config_store.store.get_configs()))
