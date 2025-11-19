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


api = FastAPI(
    title="OVPanel API",
    description="API for managing OVPanel",
    version=__version__,
    docs_url="/doc" if config.DOC else None,
)

frontend_build_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")

api.mount(
    f"/{config.URLPATH}/assets",
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
    """This function starts the scheduler for every 5 minutes tasks"""
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        check_user_expiry_date,
        CronTrigger(minute="*/5"),
        id="check_user_expiry",
        replace_existing=True,
    )

    scheduler.start()


@api.on_event("startup")
async def startup_event():
    start_scheduler()


for router in all_routers:
    api.include_router(prefix="/api", router=router)


@api.get(f"/{config.URLPATH}/{{path:path}}")
@api.get(f"/{config.URLPATH}")
async def serve_react():
    index_path = os.path.join(frontend_build_path, "index.html")
    return FileResponse(index_path)
