from fastapi.responses import Response
from sqlalchemy.orm import Session

from backend.logger import logger
from backend.schema._input import NodeCreate
from .requests import NodeRequests
from backend.db import crud
from .health_check import HealthCheckService
from .sync import SyncService


async def add_node_handler(request: NodeCreate, db: Session) -> bool:
    """Add a new node with health check."""
    new_node = NodeRequests(
        request.address,
        request.port,
        request.key,
        request.tunnel_address,
        request.protocol,
        request.ovpn_port,
        request.set_new_setting,
    )
    is_healthy, response_time = new_node.check_node()
    
    if is_healthy:
        # Create node in database
        node = crud.create_node(db, request)
        
        # Update health status
        crud.update_node_health(
            db, node.id, is_healthy=True, response_time=response_time
        )
        
        # Mark as needing sync
        crud.update_node_sync_status(db, node.id, "never_synced")
        
        logger.info(f"Node added successfully: {request.address}:{request.port}")
        
        # Sync all users to new node in background
        sync_service = SyncService(db)
        await sync_service.sync_all_users_to_node(node)
        
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
    """Retrieve all nodes with health status."""
    nodes_list = []
    nodes = crud.get_all_nodes(db)
    for node in nodes:
        # Determine actual status based on health and status
        is_active = node.status and node.is_healthy
        
        node_info = {
            "name": node.name,
            "address": node.address,
            "tunnel-address": node.tunnel_address,
            "ovpn_port": node.ovpn_port,
            "protocol": node.protocol,
            "port": node.port,
            "status": "active" if is_active else "inactive",
            "is_healthy": node.is_healthy,
            "response_time": node.response_time,
            "last_health_check": str(node.last_health_check) if node.last_health_check else None,
            "sync_status": node.sync_status,
            "last_sync_time": str(node.last_sync_time) if node.last_sync_time else None,
            "consecutive_failures": node.consecutive_failures,
        }
        nodes_list.append(node_info)
    return nodes_list


async def create_user_on_all_nodes(name: str, db: Session):
    """Create a user on all healthy nodes only."""
    sync_service = SyncService(db)
    results = await sync_service.sync_user_to_all_nodes(name)
    
    # Log summary
    success_count = sum(1 for r in results if r.get("success"))
    total_nodes = len(results)
    
    logger.info(
        f"User '{name}' created on {success_count}/{total_nodes} healthy nodes"
    )
    
    return results


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
    """Download OVPN client from a specific node with health check."""
    node = crud.get_node_by_address(db, node_address)
    
    if not node:
        logger.error(f"Node not found: {node_address}")
        return None
    
    # Check if node is healthy before allowing download
    if not node.is_healthy or not node.status:
        logger.warning(
            f"Cannot download from unhealthy node {node_address}. "
            f"Status: {node.status}, Healthy: {node.is_healthy}"
        )
        return None
    
    # Check sync status
    if node.sync_status not in ["synced", "pending"]:
        logger.warning(
            f"Node {node_address} has sync_status '{node.sync_status}', "
            f"may not have latest data"
        )
    
    result = NodeRequests(
        address=node.address, port=node.port, api_key=node.key
    ).download_ovpn_client(f"{name}-{node.name}")
    
    if result:
        logger.info(
            f"OVPN client downloaded for user '{name}-{node.name}' on node {node.address}:{node.port}"
        )
        return result
    
    logger.error(
        f"Failed to download OVPN for user '{name}-{node.name}' from node {node.address}"
    )
    return None


async def download_ovpn_from_best_node(name: str, db: Session) -> Response | None:
    """Download OVPN from the best available node."""
    best_node = crud.get_best_node_for_download(db)
    
    if not best_node:
        logger.error("No healthy nodes available for download")
        return None
    
    logger.info(f"Selected best node {best_node.address} for download")
    return await download_ovpn_client_from_node(name, best_node.address, db)


async def delete_user_on_all_nodes(name: str, db: Session):
    """Delete a user from all nodes (even unhealthy ones to cleanup)."""
    sync_service = SyncService(db)
    results = await sync_service.delete_user_from_all_nodes(name)
    
    # Log summary
    success_count = sum(1 for r in results if r.get("success"))
    total_nodes = len(results)
    
    logger.info(
        f"User '{name}' deleted from {success_count}/{total_nodes} nodes"
    )
    
    return results
