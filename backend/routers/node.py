from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.auth.auth import get_current_user
from backend.db.engine import get_db
from backend.schema.output import ResponseModel
from backend.schema._input import NodeCreate
from backend.node.task import (
    add_node_handler,
    update_node_handler,
    delete_node_handler,
    download_ovpn_client_from_node,
    list_nodes_handler,
    get_node_status_handler,
)

router = APIRouter(prefix="/node", tags=["Nodes"])


@router.post("/add", response_model=ResponseModel)
async def add_node(
    request: NodeCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    new_node = await add_node_handler(request, db)
    return ResponseModel(
        success=new_node,
        msg="Node added successfully" if new_node else "Failed to add node",
    )


@router.put("/update/{address}", response_model=ResponseModel)
async def update_node(
    address: str,
    request: NodeCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    result = await update_node_handler(address, request, db)
    return ResponseModel(
        success=result,
        msg="Node updated successfully" if result else "Failed to update node",
    )


@router.get("/status/{address}", response_model=ResponseModel)
async def get_node_status(
    address: str,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    node_status = await get_node_status_handler(address, db)
    return ResponseModel(
        success=True,
        msg="Node status retrieved successfully",
        data=node_status,
    )


@router.get("/list", response_model=ResponseModel)
async def list_nodes(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    nodes = await list_nodes_handler(db)
    return ResponseModel(
        success=True,
        msg="Nodes retrieved successfully",
        data=nodes,
    )


@router.get(
    "/download/ovpn/{address}/{name}",
    description="Download OVPN client configuration from a node",
)
async def download_ovpn_client(
    address: str,
    name: str,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    response = await download_ovpn_client_from_node(db=db, node_address=address, name=name)
    if response:
        return response
    else:
        return ResponseModel(success=False, msg="OVPN file not found", data=None)


@router.delete("/delete/{address}", response_model=ResponseModel)
async def delete_node(
    address: str,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    result = await delete_node_handler(address, db)
    return ResponseModel(
        success=result,
        msg="Node deleted successfully" if result else "Failed to delete node",
    )
