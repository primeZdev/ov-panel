from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.operations.daily_checks import check_user_expiry_date
from backend.schema.output import ResponseModel, Users
from backend.schema._input import CreateUser, UpdateUser
from backend.db.engine import get_db
from backend.db import crud
from backend.auth.auth import get_current_user
from backend.node.task import (
    delete_user_on_all_nodes,
    change_user_status_on_all_nodes,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=ResponseModel)
async def get_all_users(
    db: Session = Depends(get_db), user: dict = Depends(get_current_user)
):
    if user["type"] == "main_admin":
        all_users = crud.get_all_users(db)
        users_list = [Users.from_orm(user) for user in all_users]
        return ResponseModel(
            success=True,
            msg="Users retrieved successfully",
            data=users_list,
        )

    elif user["type"] == "admin":
        admin_users = crud.get_users_by_admin(db, admin_username=user["username"])
        users_list = [Users.from_orm(u) for u in admin_users]
        return ResponseModel(
            success=True,
            msg="Users retrieved successfully",
            data=users_list,
        )

    return ResponseModel(
        success=False,
        msg="Unauthorized access",
    )


@router.post("/", response_model=ResponseModel)
async def create_user(
    request: CreateUser,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    check_user = crud.get_user_by_name(db, request.name)
    if check_user is not None:
        return ResponseModel(
            success=False, msg="User with this name already exists", data=None
        )

    if user["type"] == "admin":
        crud.create_user(db, request, user["username"])
        return ResponseModel(success=True, msg="User created successfully", data=None)

    crud.create_user(db, request, "owner")
    return ResponseModel(
        success=True, msg="User created successfully", data=request.name
    )


@router.put("/{uuid}", response_model=ResponseModel)
async def update_user(
    uuid: str,
    request: UpdateUser,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    result = crud.update_user(db, uuid, request)
    check_user_expiry_date()
    return ResponseModel(success=True, msg="User updated successfully", data=result)


@router.put("/{uuid}/status", response_model=ResponseModel)
async def change_user_status(
    uuid: str,
    request: UpdateUser,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    await change_user_status_on_all_nodes(uuid, request.name, request.status, db)
    return ResponseModel(success=True, msg="Changed user status successfully")


@router.delete("/{uuid}", response_model=ResponseModel)
async def delete_user(
    uuid: str, db: Session = Depends(get_db), user: dict = Depends(get_current_user)
):
    user = crud.get_user_by_uuid(db, uuid)
    if user is None:
        return ResponseModel(success=False, msg="User not found", data=None)

    if await delete_user_on_all_nodes(user.name, db):
        crud.delete_user(db, user.name)
        return ResponseModel(success=True, msg="User deleted successfully")
    return ResponseModel(success=False, msg="Failed to delete user on all nodes")
