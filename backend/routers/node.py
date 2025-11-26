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

router = APIRouter(prefix="/nodes", tags=["Nodes"])


@router.post("/", response_model=ResponseModel)
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


@router.put("/{node_id}", response_model=ResponseModel)
async def update_node(
    node_id: int,
    request: NodeCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    result = await update_node_handler(node_id, request, db)
    return ResponseModel(
        success=result,
        msg="Node updated successfully" if result else "Failed to update node",
    )


@router.get("/{node_id}/status/", response_model=ResponseModel)
async def get_node_status(
    node_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    node_status = await get_node_status_handler(node_id, db)
    return ResponseModel(
        success=True,
        msg="Node status retrieved successfully",
        data=node_status,
    )


@router.get("/", response_model=ResponseModel)
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
    "/ovpn/{node_id}/{name}",
    description="Download OVPN client configuration from a node",
)
async def download_ovpn_client(
    node_id: int,
    name: str,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    response = await download_ovpn_client_from_node(db=db, node_id=node_id, name=name)
    if response:
        return response
    else:
        return ResponseModel(success=False, msg="OVPN file not found", data=None)


@router.delete("/{node_id}", response_model=ResponseModel)
async def delete_node(
    node_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    result = await delete_node_handler(node_id, db)
    return ResponseModel(
        success=result,
        msg="Node deleted successfully" if result else "Failed to delete node",
    )
