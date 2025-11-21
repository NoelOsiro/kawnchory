"""FastAPI app assembling modular admin API (routes + startup)."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

# Import the modularized router and startup helper
from .routes import router as admin_router
from .startup import startup as startup_hook


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan manager: run startup logic before the app serves requests.

    Using a lifespan manager avoids the deprecated `@app.on_event("startup")`
    pattern and cleanly supports async startup/shutdown logic.
    """
    await startup_hook()
    try:
        yield
    finally:
        # Call the explicit shutdown helper to close DB connections.
        try:
            from .startup import shutdown as shutdown_hook

            await shutdown_hook()
        except Exception:
            # Best-effort shutdown; swallow exceptions to avoid crashing server
            pass


app = FastAPI(title="EchoVoice Admin API", lifespan=lifespan)

# Include admin routes from `routes.py`
app.include_router(admin_router)
