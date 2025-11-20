"""Database-backed config store for segmentor configurations.

This module provides a small async ConfigStore that loads segmentor
configuration rows from a database into an in-memory dict for fast reads.
It also exposes a `reload()` method and a hook for rebuilding the
workflow when configs change.
"""
from __future__ import annotations

import asyncio
import importlib
import logging
import os
from typing import Callable, Dict

from sqlalchemy import JSON, TIMESTAMP, Boolean, Column, String, func, select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

# Logger for diagnostic messages during rebuilds
logger = logging.getLogger(__name__)


class SegmentorConfig(Base):
    """ORM model for segmentor configuration rows.

    This model maps to the "segmentor_configs" table and stores configuration
    for individual segmentors used by the application.

    Attributes:
    ----------
    segmentor_name : str
        Primary key identifying the segmentor.
    enabled : bool
        Whether the segmentor is enabled.
    metadata_ : dict
        JSON metadata for the segmentor (column name is "metadata"; attribute is
        named `metadata_` to avoid a SQLAlchemy reserved name conflict).
    updated_at : datetime
        Timestamp of last update (database-managed).
    """
    __tablename__ = "segmentor_configs"

    segmentor_name = Column(String, primary_key=True)
    enabled = Column(Boolean, nullable=False, default=True)
    # `metadata` is a reserved attribute name on Declarative classes, so
    # expose the DB column as `metadata` but use `metadata_` as the
    # attribute name to avoid SQLAlchemy conflicts.
    metadata_ = Column("metadata", JSON, nullable=False, default={})
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


def _default_database_url() -> str:
    # Prefer an explicit DATABASE_URL, fall back to a local sqlite file
    return os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./backend_segmentors.db")


class ConfigStore:
    """Database-backed in-memory cache for segmentor configurations.

    This class lazily initializes an asynchronous SQLAlchemy engine and session
    factory, loads configuration rows from the database into an in-memory
    dictionary for fast lookups, and exposes methods to reload the configs and
    register a hook that's called after a reload.

    Attributes:
    ----------
    database_url : Optional[str]
        The database URL used to construct the async engine.
    _engine : Optional[AsyncEngine]
        Lazily-initialized SQLAlchemy AsyncEngine.
    _Session : Optional[sessionmaker]
        Session factory bound to the async engine.
    _lock : asyncio.Lock
        Async lock used to serialize reload operations.
    _configs : Dict[str, dict]
        In-memory mapping of segmentor names to their config dicts.
    _on_reload : Optional[Callable[[Dict[str, dict]], None]]
        Optional callback invoked after configs are reloaded; may be a coroutine.
    """
    def __init__(self, database_url: str | None = None):
        """Initialize the ConfigStore with an optional database URL.

        Parameters
        ----------
        database_url : Optional[str]
            The database URL to use; if None, the default from
            _default_database_url() will be used.
        """
        self.database_url = database_url or _default_database_url()
        self._engine: AsyncEngine | None = None
        self._Session: sessionmaker | None = None
        self._lock = asyncio.Lock()
        self._configs: Dict[str, dict] = {}
        self._on_reload: Callable[[Dict[str, dict]], None] | None = None

    async def init_db(self):
        """Initialize the database engine and create tables if they do not exist."""
        if self._engine is None:
            # create engine lazily
            self._engine = create_async_engine(self.database_url, echo=False, future=True)
            self._Session = sessionmaker(self._engine, class_=AsyncSession, expire_on_commit=False)
            # create tables if they do not exist
            async with self._engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

    async def reload(self):
        """Reload configs from DB into an in-memory dict and call reload hook."""
        await self.init_db()
        async with self._lock:
            async with self._Session() as session:
                result = await session.execute(select(SegmentorConfig))
                rows = result.scalars().all()
                new_configs = {
                    r.segmentor_name: {
                        "enabled": bool(r.enabled),
                        "metadata": (getattr(r, "metadata_", None) or {}),
                    }
                    for r in rows
                }
                self._configs = new_configs

        # call hook without holding the lock
        if self._on_reload:
            maybe_coro = self._on_reload(self._configs)
            if asyncio.iscoroutine(maybe_coro):
                await maybe_coro

    def get_configs(self) -> Dict[str, dict]:
        """Return the current in-memory configs (fast, non-blocking)."""
        return dict(self._configs)

    def register_on_reload(self, cb: Callable[[Dict[str, dict]], None]):
        """Register a callback to be invoked after configs are reloaded."""
        self._on_reload = cb


# Module-level instance for convenience
store = ConfigStore()


async def rebuild_workflow_from_store(configs: Dict[str, dict] | None = None):
    """Build a new workflow based on enabled segmentors found in `configs`.

    This function is intentionally small: it determines the enabled segment
    names from the configs, calls into `workflow_graph.create_workflow`, and
    atomically swaps the module-level workflow via `workflow_graph.replace_workflow`.
    """
    if configs is None:
        configs = store.get_configs()
    enabled = {name for name, v in configs.items() if v.get("enabled")}
    # map logical names to node ids used by the workflow_graph
    # we expect segmentor names like 'behavior_seg', 'profile_seg', etc.
    # Import here to avoid circular imports at module import time. Try a
    # few likely import paths and choose the one that exposes
    # `create_workflow` so this function works regardless of how the
    # package was imported (e.g., `backend.src...` vs top-level `agent`).
    candidates = [
        "agent.graph.workflow_graph",
        "backend.src.agent.graph.workflow_graph",
        "src.agent.graph.workflow_graph",
    ]

    workflow_graph = None
    last_exc = None
    tried = []
    for name in candidates:
        tried.append(name)
        try:
            logger.debug("Attempting to import workflow_graph module '%s'", name)
            mod = importlib.import_module(name)
        except Exception as exc:  # pylint: disable=broad-except
            logger.debug("Import failed for %s: %s", name, exc)
            last_exc = exc
            mod = None
        if mod is None:
            continue
        # If the module was imported but doesn't expose the expected
        # attribute (possible with circular imports), try reloading it.
        if not hasattr(mod, "create_workflow"):
            try:
                logger.debug("Reloading module %s to resolve partial initialization", name)
                importlib.reload(mod)
            except Exception as exc:  # pylint: disable=broad-except
                logger.debug("Reload failed for %s: %s", name, exc)
                last_exc = exc
        if hasattr(mod, "create_workflow"):
            workflow_graph = mod
            logger.debug("Found workflow_graph in %s", name)
            break

    # Last-resort attempts: try package-relative import or direct import
    if workflow_graph is None:
        try:
            logger.debug("Attempting package-relative import 'agent.graph.workflow_graph'")
            from agent.graph import workflow_graph as wf  # type: ignore

            try:
                importlib.reload(wf)
            except Exception as exc:  # pylint: disable=broad-except
                logger.debug("Reload failed for agent.graph.workflow_graph: %s", exc)
            if hasattr(wf, "create_workflow"):
                workflow_graph = wf
                logger.debug("Found workflow_graph via package-relative import")
        except Exception as exc:  # pylint: disable=broad-except
            logger.debug("Package-relative import failed: %s", exc)
            last_exc = exc

    if workflow_graph is None:
        # Provide a helpful error with diagnostics
        msg = (
            f"Could not locate workflow_graph.create_workflow. Tried: {', '.join(tried)}. "
            f"Last exception: {repr(last_exc)}"
        )
        logger.error(msg)
        raise RuntimeError(msg)

    try:
        logger.info("Building new workflow with enabled segments: %s", sorted(enabled))
        new_wf = workflow_graph.create_workflow(compiled=True, enabled_segments=enabled)
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Failed to create workflow using %s: %s", getattr(workflow_graph, "__name__", workflow_graph), exc)
        raise

    try:
        workflow_graph.replace_workflow(new_wf)
        logger.info("Replaced module-level workflow via %s", getattr(workflow_graph, "__name__", workflow_graph))
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Failed to replace module-level workflow: %s", exc)
        raise
