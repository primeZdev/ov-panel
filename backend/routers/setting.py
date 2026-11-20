from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
import httpx

from backend.db.engine import get_db
from backend.db import crud
from backend.auth.auth import get_current_user
from backend.operations.server_info import get_server_info
from backend.schema.output import Settings, ServerInfo, ResponseModel, VersionCheck
from backend.config import config
from backend.version import __version__

router = APIRouter(prefix="/server", tags=["Panel Settings"])


@router.get("/settings", response_model=ResponseModel)
async def get_settings(
    request: Request,
    db: Session = Depends(get_db),
    user: str = Depends(get_current_user),
):
    settings = Settings(
        subscription_path=config.SUBSCRIPTION_PATH,
        subscription_url_prefix=(
            config.SUBSCRIPTION_URL_PREFIX + "/"
            if config.SUBSCRIPTION_URL_PREFIX is not None
            else str(request.base_url)
        ),
    )
    return ResponseModel(
        success=True,
        msg="Settings retrieved successfully",
        data=settings,
    )


@router.get(
    "/info",
    response_model=ResponseModel,
    description="Get server information (cpu, memory, ...)",
)
async def get_server_information(user: dict = Depends(get_current_user)):
    result = await get_server_info()
    return ResponseModel(
        success=True,
        msg="Server information retrieved successfully",
        data=ServerInfo.from_orm(result),
    )


@router.get(
    "/check-update",
    response_model=ResponseModel,
    description="Check for new version on GitHub",
)
async def check_update(user: dict = Depends(get_current_user)):
    latest_version = __version__
    release_url = "https://github.com/primeZdev/ov-panel/releases/latest"
    release_notes = ""
    update_available = False

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://api.github.com/repos/primeZdev/ov-panel/releases/latest",
                headers={"Accept": "application/vnd.github.v3+json"},
            )
            if response.status_code == 200:
                data = response.json()
                latest_version = data.get("tag_name", "").lstrip("v")
                release_url = data.get("html_url", release_url)
                release_notes = data.get("body", "")[:500] if data.get("body") else ""

                current = tuple(map(int, __version__.split(".")))
                latest = tuple(map(int, latest_version.split(".")))
                update_available = latest > current
    except Exception:
        pass

    return ResponseModel(
        success=True,
        msg="Version check completed",
        data=VersionCheck(
            current_version=__version__,
            latest_version=latest_version,
            update_available=update_available,
            release_url=release_url,
            release_notes=release_notes,
        ),
    )
