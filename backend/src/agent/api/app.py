"""FastAPI app assembling modular admin API (routes + startup)."""
from __future__ import annotations

from fastapi import FastAPI

# Import the modularized router and startup helper
from .routes import router as admin_router
from .startup import startup as startup_hook

app = FastAPI(title="Kawnchory Admin API")

# Include admin routes from `routes.py`
app.include_router(admin_router)


@app.on_event("startup")
async def _startup_event() -> None:
    """Call startup helper from `startup.py` to initialize DB and schedule rebuilds."""
    await startup_hook()
