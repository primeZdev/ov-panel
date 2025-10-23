from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import uvicorn

from operations.daily_checks import check_user_expiry_date
from config import config
from routers import all_routers
from version import __version__


api = FastAPI(
    title="OVPanel API",
    description="API for managing OVPanel",
    version=__version__,
    docs_url="/doc" if config.DOC else None,
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


for router in all_routers:
    api.include_router(prefix=f"/{config.URLPATH}", router=router)

if __name__ == "__main__":
    uvicorn.run(
        "app:api",
        host="0.0.0.0",
        port=config.PORT,
        reload=True,
        ssl_keyfile=config.SSL_KEYFILE,
        ssl_certfile=config.SSL_CERTFILE,
    )
