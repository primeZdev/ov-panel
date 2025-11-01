from fastapi.responses import Response
from sqlalchemy.orm import Session

from backend.logger import logger
from backend.schema._input import NodeCreate
from .requests import NodeRequests
from backend.db import crud


async def add_node_handler(request: NodeCreate, db: Session) -> bool:
    new_node = NodeRequests(
        request.address,
        request.port,
        request.key,
        request.tunnel_address,
        request.protocol,
        request.ovpn_port,
        request.set_new_setting,
    )
    if new_node.check_node():
        crud.create_node(db, request)
        logger.info(f"Node added successfully: {request.address}:{request.port}")
        return True
    else:
        logger.warning(f"Failed to add node: {request.address}:{request.port}")
        return False


async def update_node_handler(address: str, request: NodeCreate, db: Session) -> None:
    """Update a node"""
    crud.update_node(db, address, request)
    logger.info(f"Node updated successfully: {address}")
    return True


async def delete_node_handler(address: str, db: Session) -> bool:
    """Delete a node"""
    node = crud.get_node_by_address(db, address)
    if node:
        crud.delete_node(db, node.id)
        logger.info(f"Node deleted successfully: {address}")
        return True
    else:
        logger.warning(f"Failed to delete node: {address}")
        return False


async def list_nodes_handler(db: Session) -> list:
    """Retrieve all nodes"""
    nodes_list = []
    nodes = crud.get_all_nodes(db)
    for node in nodes:
        node_info = {
            "name": node.name,
            "address": node.address,
            "tunnel-address": node.tunnel_address,
            "ovpn_port": node.ovpn_port,
            "protocol": node.protocol,
            "port": node.port,
            "status": "active" if node.status else "inactive",
        }
        nodes_list.append(node_info)
    return nodes_list


async def create_user_on_all_nodes(name: str, db: Session):
    """Create a user on all nodes"""
    nodes = crud.get_all_nodes(db)
    if nodes:
        for node in nodes:
            node_requests = NodeRequests(
                address=node.address, port=node.port, api_key=node.key
            )
            node_status = node_requests.check_node()
            if node_status:
                node_requests.create_user(f"{name}-{node.name}")
                logger.info(
                    f"User '{name}-{node.name}' created on node {node.address}:{node.port}"
                )
            else:
                logger.warning(
                    f"Failed to create user '{name}-{node.name}' on node {node.address}:{node.port}"
                )


async def get_node_status_handler(address: str, db: Session):
    """Get the status of a node"""
    node = crud.get_node_by_address(db, address)
    if node:
        node_status = NodeRequests(
            address=node.address, port=node.port, api_key=node.key
        ).get_node_info()
        return {
            "address": node.address,
            "port": node.port,
            "status": "active" if node.status else "inactive",
            "node_info": node_status,
        }
    return None


async def download_ovpn_client_from_node(
    name: str, node_address: str, db: Session
) -> Response | None:
    """Download OVPN client from a node"""
    node = crud.get_node_by_address(db, node_address)
    result = NodeRequests(
        address=node.address, port=node.port, api_key=node.key
    ).download_ovpn_client(f"{name}-{node.name}")
    if result:
        logger.info(
            f"OVPN client downloaded for user '{name}-{node.name}' on node {node.address}:{node.port}"
        )
        return result
    return None


async def delete_user_on_all_nodes(name: str, db: Session):
    """Delete a user from all nodes"""
    nodes = crud.get_all_nodes(db)
    if nodes:
        for node in nodes:
            node_requests = NodeRequests(
                address=node.address, port=node.port, api_key=node.key
            )
            node_status = node_requests.check_node()
            if node_status:
                node_requests.delete_user(f"{name}-{node.name}")
                logger.info(
                    f"User '{name}-{node.name}' deleted on node {node.address}:{node.port}"
                )
            else:
                logger.warning(
                    f"Failed to delete user '{name}-{node.name}' on node {node.address}:{node.port}"
                )
