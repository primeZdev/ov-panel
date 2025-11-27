from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from backend.db.engine import get_db
from backend.db import crud
from backend.auth.auth import get_current_user
from backend.operations.server_info import get_server_info
from backend.schema.output import Settings, ServerInfo, ResponseModel
from backend.config import config

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
