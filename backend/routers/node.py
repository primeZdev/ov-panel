from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
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
    download_ovpn_from_best_node,
    list_nodes_handler,
    get_node_status_handler,
)
from backend.node.health_check import HealthCheckService
from backend.node.sync import SyncService
from backend.logger import logger

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
    """Get all nodes with their cached health status.
    
    This endpoint returns immediately with cached health data.
    It does NOT perform live health checks to avoid blocking.
    Use /health-check/all for live health checks.
    """
    nodes = await list_nodes_handler(db)
    return ResponseModel(
        success=True,
        msg="Nodes retrieved successfully",
        data=nodes,
    )


@router.get("/list/with-status", response_model=ResponseModel)
async def list_nodes_with_live_status(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Get all nodes with their live status including CPU and memory usage.
    
    This endpoint fetches real-time status from each node.
    Use this for dashboard/monitoring views.
    """
    from backend.db import crud
    from backend.node.requests import NodeRequests
    import asyncio
    
    all_nodes = crud.get_all_nodes(db)
    
    async def fetch_node_status(node):
        """Fetch live status for a single node."""
        node_info = {
            "name": node.name,
            "address": node.address,
            "tunnel_address": node.tunnel_address,
            "ovpn_port": node.ovpn_port,
            "protocol": node.protocol,
            "port": node.port,
            "status": "offline",
            "is_healthy": False,
            "cpu_usage": None,
            "memory_usage": None,
            "node_status": None,
            "response_time": None,
            "last_health_check": str(node.last_health_check) if node.last_health_check else None,
        }
        
        # Only check if node is marked as active
        if node.status:
            try:
                node_request = NodeRequests(
                    address=node.address,
                    port=node.port,
                    api_key=node.key,
                    tunnel_addres=node.tunnel_address or "ovpanel.com",
                    protocol=node.protocol,
                    ovpn_port=node.ovpn_port,
                    timeout=3,  # Quick timeout
                    max_retries=0,  # No retries for speed
                )
                
                # Get live node info
                live_data = await node_request.get_node_info_async()
                
                if live_data:
                    node_info.update({
                        "status": "online",
                        "is_healthy": True,
                        "cpu_usage": live_data.get("cpu_usage"),
                        "memory_usage": live_data.get("memory_usage"),
                        "node_status": live_data.get("status"),
                        "response_time": round(live_data.get("response_time", 0), 3) if live_data.get("response_time") else None,
                    })
            except Exception as e:
                logger.warning(f"Failed to get live status for node {node.address}: {e}")
        
        return node_info
    
    # Fetch all node statuses concurrently
    nodes_with_status = await asyncio.gather(*[fetch_node_status(node) for node in all_nodes])
    
    # Calculate summary stats
    online_count = sum(1 for n in nodes_with_status if n["status"] == "online")
    offline_count = len(nodes_with_status) - online_count
    
    return ResponseModel(
        success=True,
        msg="Nodes with live status retrieved successfully",
        data={
            "nodes": nodes_with_status,
            "summary": {
                "total": len(nodes_with_status),
                "online": online_count,
                "offline": offline_count,
            }
        },
    )


@router.get("/list/healthy", response_model=ResponseModel)
async def list_healthy_nodes(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Get only healthy and active nodes for download selection."""
    from backend.db import crud
    
    all_nodes = crud.get_all_nodes(db)
    healthy_nodes = [
        {
            "name": node.name,
            "address": node.address,
            "response_time": round(node.response_time, 3) if node.response_time else None,
        }
        for node in all_nodes
        if node.status and node.is_healthy
    ]
    
    return ResponseModel(
        success=True,
        msg=f"Found {len(healthy_nodes)} healthy nodes",
        data=healthy_nodes,
    )


@router.get(
    "/download/ovpn/{address}/{name}",
    description="Download OVPN client configuration from a specific node",
)
async def download_ovpn_client(
    address: str,
    name: str,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Download OVPN from specific node with health validation."""
    response = await download_ovpn_client_from_node(
        name=name, node_address=address, db=db
    )
    if response:
        return response
    else:
        # Get node to provide better error message
        from backend.db import crud
        node = crud.get_node_by_address(db, address)
        
        if not node:
            raise HTTPException(status_code=404, detail="Node not found")
        elif not node.status:
            raise HTTPException(status_code=400, detail="Node is inactive")
        elif not node.is_healthy:
            raise HTTPException(
                status_code=503,
                detail=f"Node is unhealthy (last check: {node.last_health_check})"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to download OVPN file from node"
            )


@router.get(
    "/download/ovpn/best/{name}",
    description="Download OVPN client configuration from the best available node",
)
async def download_ovpn_from_best(
    name: str,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Download OVPN from the best performing healthy node."""
    response = await download_ovpn_from_best_node(name=name, db=db)
    if response:
        return response
    else:
        raise HTTPException(
            status_code=503,
            detail="No healthy nodes available for download. Please try again later or contact administrator."
        )


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


# Health Check Endpoints
@router.post("/health-check/all", response_model=ResponseModel)
async def health_check_all_nodes(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Run health check on all nodes."""
    health_service = HealthCheckService(db)
    results = await health_service.check_all_nodes()
    
    healthy_count = sum(1 for r in results if r.get("is_healthy"))
    
    return ResponseModel(
        success=True,
        msg=f"Health check completed: {healthy_count}/{len(results)} nodes healthy",
        data=results,
    )


@router.post("/health-check/{address}", response_model=ResponseModel)
async def health_check_node(
    address: str,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Run health check on a specific node."""
    from backend.db import crud
    
    node = crud.get_node_by_address(db, address)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    
    health_service = HealthCheckService(db)
    result = await health_service.check_node_health(node)
    
    return ResponseModel(
        success=result.get("is_healthy", False),
        msg=f"Node is {'healthy' if result.get('is_healthy') else 'unhealthy'}",
        data=result,
    )


@router.post("/recover", response_model=ResponseModel)
async def recover_nodes(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Attempt to recover unhealthy nodes."""
    health_service = HealthCheckService(db)
    recovered = await health_service.auto_recover_nodes()
    
    return ResponseModel(
        success=True,
        msg=f"Recovery completed: {len(recovered)} nodes recovered",
        data=recovered,
    )


# Sync Endpoints
@router.post("/sync/all", response_model=ResponseModel)
async def sync_all_nodes(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Synchronize all users to all healthy nodes."""
    sync_service = SyncService(db)
    results = await sync_service.sync_all_nodes()
    
    total_synced = sum(r.get("synced", 0) for r in results)
    total_failed = sum(r.get("failed", 0) for r in results)
    
    return ResponseModel(
        success=True,
        msg=f"Sync completed: {total_synced} users synced, {total_failed} failed",
        data=results,
    )


@router.post("/sync/pending", response_model=ResponseModel)
async def sync_pending_nodes(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Synchronize only nodes with pending sync status."""
    sync_service = SyncService(db)
    results = await sync_service.sync_pending_nodes()
    
    return ResponseModel(
        success=True,
        msg=f"Pending sync completed for {len(results)} nodes",
        data=results,
    )


@router.post("/sync/{address}", response_model=ResponseModel)
async def sync_single_node(
    address: str,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Synchronize all users to a specific node."""
    from backend.db import crud
    
    node = crud.get_node_by_address(db, address)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    
    if not node.is_healthy or not node.status:
        raise HTTPException(
            status_code=400,
            detail="Cannot sync to unhealthy or inactive node"
        )
    
    sync_service = SyncService(db)
    result = await sync_service.sync_all_users_to_node(node)
    
    return ResponseModel(
        success=result.get("failed", 0) == 0,
        msg=f"Sync completed: {result.get('synced', 0)} users synced",
        data=result,
    )


# Scheduler Management Endpoints
@router.get("/scheduler/status", response_model=ResponseModel)
async def get_scheduler_status(
    user: dict = Depends(get_current_user),
):
    """Get scheduler status and scheduled jobs."""
    from backend.node.scheduler import scheduler
    
    jobs = scheduler.get_jobs()
    
    return ResponseModel(
        success=True,
        msg="Scheduler status retrieved",
        data={
            "is_running": scheduler.is_running,
            "jobs": jobs,
        },
    )
