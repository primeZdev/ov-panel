import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.operations.daily_checks import check_user_expiry_date
from backend.config import config
from backend.routers import all_routers
from backend.version import __version__
from backend.node.scheduler import scheduler as node_scheduler
from backend.logger import logger


api = FastAPI(
    title="OVPanel API",
    description="API for managing OVPanel",
    version=__version__,
    docs_url="/doc" if config.DOC else None,
)

frontend_build_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")

api.mount(
    "/assets",
    StaticFiles(directory=os.path.join(frontend_build_path, "assets")),
    name="assets",
)

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def start_scheduler():
    """This function starts the scheduler for daily tasks"""
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        check_user_expiry_date,
        CronTrigger(hour=0, minute=0),
        id="check_user_expiry",
        replace_existing=True,
    )

    scheduler.start()


@api.on_event("startup")
async def startup_event():
    start_scheduler()
    
    # Start node health check and sync scheduler
    try:
        node_scheduler.start()
        logger.info("Node health check and sync scheduler started")
    except Exception as e:
        logger.error(f"Failed to start node scheduler: {e}")


@api.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    try:
        node_scheduler.stop()
        logger.info("Node scheduler stopped")
    except Exception as e:
        logger.error(f"Error stopping node scheduler: {e}")


@api.get(f"/{config.URLPATH}")
async def serve_react():
    index_path = os.path.join(frontend_build_path, "index.html")
    return FileResponse(index_path)


for router in all_routers:
    api.include_router(prefix="/api", router=router)


# Catch-all route for SPA routing - must be AFTER all API routes
@api.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    """Serve React app for all non-API routes to support client-side routing."""
    # Don't serve index.html for API routes or assets
    if full_path.startswith("api/") or full_path.startswith("assets/"):
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Not found")
    
    # Serve index.html for all other routes
    index_path = os.path.join(frontend_build_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail="Frontend not built")
