"""Health check service for monitoring node status."""

from sqlalchemy.orm import Session
from backend.db import crud
from backend.node.requests import NodeRequests
from backend.logger import logger
from typing import List
import asyncio


class HealthCheckService:
    """Service for checking node health and updating status."""

    def __init__(self, db: Session):
        self.db = db

    async def check_node_health(self, node) -> dict:
        """Check health of a single node.
        
        Returns:
            dict with health status information
        """
        try:
            node_request = NodeRequests(
                address=node.address,
                port=node.port,
                api_key=node.key,
                timeout=5,  # 5 second timeout for health checks
                max_retries=1,  # Only 1 retry for health checks
            )
            
            is_healthy, response_time = node_request.check_node()
            
            # Update consecutive failures
            if is_healthy:
                consecutive_failures = 0
            else:
                consecutive_failures = node.consecutive_failures + 1
            
            # Update node health in database
            crud.update_node_health(
                self.db,
                node.id,
                is_healthy=is_healthy,
                response_time=response_time,
                consecutive_failures=consecutive_failures,
            )
            
            logger.info(
                f"Health check for node {node.address}: "
                f"{'healthy' if is_healthy else 'unhealthy'} "
                f"(response_time: {response_time}s, failures: {consecutive_failures})"
            )
            
            return {
                "node_id": node.id,
                "address": node.address,
                "is_healthy": is_healthy,
                "response_time": response_time,
                "consecutive_failures": consecutive_failures,
            }
            
        except Exception as e:
            logger.error(f"Error checking health for node {node.address}: {e}")
            
            # Mark as unhealthy on exception
            consecutive_failures = node.consecutive_failures + 1
            crud.update_node_health(
                self.db,
                node.id,
                is_healthy=False,
                response_time=None,
                consecutive_failures=consecutive_failures,
            )
            
            return {
                "node_id": node.id,
                "address": node.address,
                "is_healthy": False,
                "response_time": None,
                "consecutive_failures": consecutive_failures,
                "error": str(e),
            }

    async def check_all_nodes(self) -> List[dict]:
        """Check health of all nodes.
        
        Returns:
            List of health check results
        """
        nodes = crud.get_all_nodes(self.db)
        
        if not nodes:
            logger.info("No nodes found for health check")
            return []
        
        logger.info(f"Starting health check for {len(nodes)} nodes")
        
        # Check all nodes concurrently
        tasks = [self.check_node_health(node) for node in nodes]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and count healthy nodes
        valid_results = [r for r in results if isinstance(r, dict)]
        healthy_count = sum(1 for r in valid_results if r.get("is_healthy"))
        
        logger.info(
            f"Health check completed: {healthy_count}/{len(valid_results)} nodes healthy"
        )
        
        return valid_results

    async def auto_recover_nodes(self) -> List[dict]:
        """Attempt to recover nodes that were previously unhealthy.
        
        Returns:
            List of nodes that recovered
        """
        # Get nodes that are inactive but might have recovered
        all_nodes = crud.get_all_nodes(self.db)
        unhealthy_nodes = [n for n in all_nodes if not n.is_healthy or not n.status]
        
        if not unhealthy_nodes:
            return []
        
        logger.info(f"Attempting to recover {len(unhealthy_nodes)} unhealthy nodes")
        
        recovered_nodes = []
        for node in unhealthy_nodes:
            result = await self.check_node_health(node)
            if result.get("is_healthy"):
                # Reset consecutive failures and mark as active
                node.status = True
                node.sync_status = "pending"  # Need to sync after recovery
                self.db.commit()
                
                recovered_nodes.append(result)
                logger.info(f"Node {node.address} recovered successfully")
        
        if recovered_nodes:
            logger.info(f"Successfully recovered {len(recovered_nodes)} nodes")
        
        return recovered_nodes
