from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.schema.output import ResponseModel, Users
from backend.schema._input import CreateUser, UpdateUser
from backend.db.engine import get_db
from backend.db import crud
from backend.operations.user_management import (
    create_user_on_server,
    delete_user_on_server,
    download_ovpn_file,
)
from backend.auth.auth import get_current_user
from backend.node.task import (
    create_user_on_all_nodes,
    delete_user_on_all_nodes,
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


@router.get("/download/ovpn/{name}")
async def download_ovpn(
    name: str,
    user: dict = Depends(get_current_user),
):
    response = download_ovpn_file(name)
    if response:
        return FileResponse(
            path=response,
            filename=f"{name}.ovpn",
            media_type="application/x-openvpn-profile",
        )
    else:
        return ResponseModel(success=False, msg="OVPN file not found", data=None)


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

    server_result = create_user_on_server(request.name, request.expiry_date)
    if not server_result:
        return ResponseModel(
            success=False, msg="Server error while creating user", data=None
        )

    await create_user_on_all_nodes(request.name, db)
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


@router.delete("/delete/{name}")
async def delete_user(
    name: str, db: Session = Depends(get_db), user: dict = Depends(get_current_user)
):
    server_result = delete_user_on_server(name)
    if server_result == "not_found":
        return ResponseModel(success=False, msg="User not found on server", data=None)

    await delete_user_on_all_nodes(name, db)
    db_result = crud.delete_user(db, name)
    return ResponseModel(success=True, msg="User deleted successfully", data=db_result)
