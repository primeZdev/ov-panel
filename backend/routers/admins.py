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
    users = crud.get_all_users(db)

    admin_list = []
    for admin in result:
        admin_data = Admins.from_orm(admin)
        admin_data.users_count = sum(1 for u in users if u.owner == admin.username)
        admin_list.append(admin_data)

    return ResponseModel(
        success=True,
        msg="Admins retrieved successfully",
        data=admin_list,
    )


@router.post("/", response_model=ResponseModel)
async def create_admin(
    admin: AdminCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    if user["type"] != "main_admin":
        return ResponseModel(
            success=False, msg="You do not have permission for this action", data=None
        )

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
    if user["type"] != "main_admin":
        return ResponseModel(
            success=False, msg="You do not have permission for this action", data=None
        )

    existing_admin = crud.get_admin_by_username(db, username=admin.username)
    if not existing_admin:
        return ResponseModel(success=False, msg="Admin not found", data=None)

    updated_admin = crud.update_admin(db, existing_admin, admin)
    return ResponseModel(
        success=True,
        msg="Admin updated successfully",
        data=Admins.from_orm(updated_admin),
    )


@router.delete("/{username}")
async def delete_admin(
    username: str,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    if user["type"] != "main_admin":
        return ResponseModel(
            success=False, msg="You do not have permission for this action", data=None
        )

    existing_admin = crud.get_admin_by_username(db, username=username)
    if not existing_admin:
        return ResponseModel(success=False, msg="Admin not found", data=None)

    crud.delete_admin(db, existing_admin)
    return ResponseModel(
        success=True,
        msg="Admin deleted successfully",
        data=None,
    )
