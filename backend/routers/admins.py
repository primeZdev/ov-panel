from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.db.engine import get_db
from backend.db import crud
from backend.schema.output import Admins, ResponseModel
from backend.schema._input import AdminCreate
from backend.auth.auth import get_current_user


router = APIRouter(prefix="/admin", tags=["Admins"])


@router.get("/", response_model=ResponseModel)
async def get_all_admins(
    db: Session = Depends(get_db), user: dict = Depends(get_current_user)
):
    result = crud.get_all_admins(db)
    return ResponseModel(
        success=True,
        msg="Admins retrieved successfully",
        data=[Admins.from_orm(admin) for admin in result],
    )


@router.post("/", response_model=ResponseModel)
async def create_admin(
    admin: AdminCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    existing_admin = crud.get_admin_by_username(db, username=admin.username)
    if existing_admin:
        return ResponseModel(
            success=False, msg="Admin with this username already exists", data=None
        )

    new_admin = crud.create_admin(db, admin)
    return ResponseModel(
        success=True,
        msg="Admin created successfully",
        data=Admins.from_orm(new_admin),
    )


@router.put("/")
async def update_admin(
    admin: AdminCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    existing_admin = crud.get_admin_by_username(db, username=admin.username)
    if not existing_admin:
        return ResponseModel(success=False, msg="Admin not found", data=None)

    updated_admin = crud.update_admin(db, existing_admin, admin)
    return ResponseModel(
        success=True,
        msg="Admin updated successfully",
        data=Admins.from_orm(updated_admin),
    )
