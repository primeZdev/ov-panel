from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.db.engine import get_db
from backend.db import crud
from backend.auth.auth import get_current_user
from backend.operations.server_info import get_server_info
from backend.schema.output import Settings, ServerInfo, ResponseModel

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
