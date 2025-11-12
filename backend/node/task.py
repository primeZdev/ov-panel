from fastapi.responses import Response
from sqlalchemy.orm import Session
import asyncio

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
        timeout=5,
        max_retries=1,
    )
    
    # Use async health check
    is_healthy, response_time = await new_node.check_node_async()
    
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
        
        # Sync all users to new node in background (don't await)
        asyncio.create_task(_sync_node_background(node.id, db))
        
        return True
    else:
        logger.warning(f"Failed to add node - unhealthy: {request.address}:{request.port}")
        return False


async def _sync_node_background(node_id: int, db: Session):
    """Background task to sync node."""
    try:
        node = crud.get_node_by_id(db, node_id)
        if node:
            sync_service = SyncService(db)
            await sync_service.sync_all_users_to_node(node)
    except Exception as e:
        logger.error(f"Background sync failed for node {node_id}: {e}")


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
    """Retrieve all nodes with current health status from database only.
    
    Does NOT perform health checks here to avoid blocking.
    Health checks are done by scheduled background tasks.
    """
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
            "response_time": round(node.response_time, 3) if node.response_time else None,
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
    """Get the status of a node with quick async check."""
    node = crud.get_node_by_address(db, address)
    if not node:
        return None
    
    # Only fetch fresh status if node is marked healthy
    node_info = {}
    if node.is_healthy and node.status:
        try:
            node_request = NodeRequests(
                address=node.address,
                port=node.port,
                api_key=node.key,
                timeout=3,  # Quick timeout
                max_retries=0,  # No retries
            )
            node_info = await node_request.get_node_info_async()
        except Exception as e:
            logger.warning(f"Failed to get live info for node {address}: {e}")
            node_info = {"error": "Failed to fetch live data"}
    
    return {
        "address": node.address,
        "port": node.port,
        "status": "active" if (node.status and node.is_healthy) else "inactive",
        "is_healthy": node.is_healthy,
        "last_health_check": str(node.last_health_check) if node.last_health_check else None,
        "response_time": node.response_time,
        "node_info": node_info,
    }


async def download_ovpn_client_from_node(
    name: str, node_address: str, db: Session
) -> Response | None:
    """Download OVPN client from a specific node with health check."""
    node = crud.get_node_by_address(db, node_address)
    
    if not node:
        logger.error(f"Node not found: {node_address}")
        return None
    
    # CRITICAL: Check if node is healthy before allowing download
    if not node.is_healthy:
        logger.warning(
            f"Cannot download from unhealthy node {node_address}. "
            f"Health status: {node.is_healthy}, Last check: {node.last_health_check}"
        )
        return None
    
    if not node.status:
        logger.warning(f"Cannot download from inactive node {node_address}")
        return None
    
    # Check sync status - warn but allow if synced or pending
    if node.sync_status not in ["synced", "pending"]:
        logger.warning(
            f"Node {node_address} has sync_status '{node.sync_status}', "
            f"may not have latest data. Last sync: {node.last_sync_time}"
        )
    
    try:
        # Use short timeout for download attempt
        result = NodeRequests(
            address=node.address,
            port=node.port,
            api_key=node.key,
            timeout=10,  # 10 seconds for download
            max_retries=0,
        ).download_ovpn_client(f"{name}-{node.name}")
        
        if result:
            logger.info(
                f"OVPN client downloaded for user '{name}-{node.name}' from node {node.address}"
            )
            return result
        
        # If download failed, mark node as potentially unhealthy
        logger.error(
            f"Failed to download OVPN for user '{name}-{node.name}' from node {node.address}"
        )
        crud.update_node_health(
            db,
            node.id,
            is_healthy=False,
            consecutive_failures=node.consecutive_failures + 1,
        )
        
    except Exception as e:
        logger.error(f"Exception downloading from node {node_address}: {e}")
        crud.update_node_health(
            db,
            node.id,
            is_healthy=False,
            consecutive_failures=node.consecutive_failures + 1,
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
