from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.engine import get_db
from db import crud
from auth.auth import get_current_user
from operations.server_info import get_server_info
from schema._input import SettingsUpdate
from schema.output import Settings, ServerInfo, ResponseModel
from operations.core_setting import change_config

router = APIRouter(prefix="/settings", tags=["Panel Settings"])


@router.get("/", response_model=ResponseModel)
async def get_settings(
    db: Session = Depends(get_db), user: str = Depends(get_current_user)
):
    settings = crud.get_settings(db)
    return ResponseModel(
        success=True,
        msg="Settings retrieved successfully",
        data=Settings.from_orm(settings),
    )


@router.put("/update", response_model=ResponseModel)
async def update_settings(
    request: SettingsUpdate,
    db: Session = Depends(get_db),
    user: str = Depends(get_current_user),
):
    update = crud.update_settings(db, request)
    if update:
        set_new_conf = change_config(request)
        if not set_new_conf:
            return ResponseModel(success=False, msg="Failed to apply new configuration")
    return ResponseModel(success=True, msg="Settings updated successfully")


@router.get(
    "/server/info",
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
