from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.db.engine import get_db
from backend.db import crud
from backend.schema.output import Admins, ResponseModel
from backend.auth.auth import get_current_user


router = APIRouter(prefix="/admin", tags=["Admins"])


@router.get("/all", response_model=ResponseModel)
async def get_all_admins(
    db: Session = Depends(get_db), user: dict = Depends(get_current_user)
):
    result = crud.get_all_admins(db)
    return ResponseModel(
        success=True,
        msg="Admins retrieved successfully",
        data=[Admins.from_orm(admin) for admin in result],
    )


# @router.post("/create")
# async def create_admin():
#     pass


# @router.put("/update")
# async def update_admin():
#     pass
