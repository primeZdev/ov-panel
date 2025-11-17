from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.schema.output import ResponseModel, Users
from backend.schema._input import CreateUser, UpdateUser
from backend.db.engine import get_db
from backend.db import crud
from backend.auth.auth import get_current_user
from backend.node.task import (
    delete_user_on_all_nodes,
    change_user_status_on_all_nodes,
)

router = APIRouter(prefix="/user", tags=["Users"])


@router.get("/all", response_model=ResponseModel)
async def get_all_users(
    db: Session = Depends(get_db), user: dict = Depends(get_current_user)
):
    all_users = crud.get_all_users(db)
    users_list = [Users.from_orm(user) for user in all_users]
    return ResponseModel(
        success=True,
        msg="Users retrieved successfully",
        data=users_list,
    )


@router.post("/create", response_model=ResponseModel)
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

    crud.create_user(db, request, "owner")
    return ResponseModel(
        success=True, msg="User created successfully", data=request.name
    )


@router.put("/update")
async def update_user(
    request: UpdateUser,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    result = crud.update_user(db, request)
    return ResponseModel(success=True, msg="User updated successfully", data=result)


@router.put("/change-status", response_model=ResponseModel)
async def change_user_status(
    request: UpdateUser,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    await change_user_status_on_all_nodes(request.name, request.status, db)
    return ResponseModel(success=True, msg="Changed user status successfully")


@router.delete("/delete/{name}")
async def delete_user(
    name: str, db: Session = Depends(get_db), user: dict = Depends(get_current_user)
):
    if await delete_user_on_all_nodes(name, db):
        crud.delete_user(db, name)
        return ResponseModel(success=True, msg="User deleted successfully")
    return ResponseModel(success=False, msg="Failed to delete user on all nodes")
