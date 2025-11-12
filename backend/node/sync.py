"""Synchronization service for keeping nodes in sync."""

from sqlalchemy.orm import Session
from backend.db import crud
from backend.node.requests import NodeRequests
from backend.logger import logger
from typing import List, Dict
import asyncio


class SyncService:
    """Service for synchronizing data between nodes."""

    def __init__(self, db: Session):
        self.db = db

    async def sync_user_to_node(self, user_name: str, node) -> dict:
        """Sync a single user to a node.
        
        Returns:
            dict with sync result
        """
        try:
            node_request = NodeRequests(
                address=node.address,
                port=node.port,
                api_key=node.key,
                timeout=10,
                max_retries=2,
            )
            
            # Create user with node-specific name
            user_name_with_node = f"{user_name}-{node.name}"
            success = node_request.create_user(user_name_with_node)
            
            if success:
                logger.info(f"Synced user '{user_name_with_node}' to node {node.address}")
                return {
                    "node_id": node.id,
                    "address": node.address,
                    "user": user_name,
                    "success": True,
                }
            else:
                logger.warning(
                    f"Failed to sync user '{user_name_with_node}' to node {node.address}"
                )
                return {
                    "node_id": node.id,
                    "address": node.address,
                    "user": user_name,
                    "success": False,
                }
                
        except Exception as e:
            logger.error(f"Error syncing user '{user_name}' to node {node.address}: {e}")
            return {
                "node_id": node.id,
                "address": node.address,
                "user": user_name,
                "success": False,
                "error": str(e),
            }

    async def sync_all_users_to_node(self, node) -> dict:
        """Sync all users from database to a specific node.
        
        Returns:
            dict with sync statistics
        """
        try:
            # Get all active users from database
            users = crud.get_all_users(self.db)
            
            if not users:
                logger.info(f"No users to sync to node {node.address}")
                return {
                    "node_id": node.id,
                    "address": node.address,
                    "total_users": 0,
                    "synced": 0,
                    "failed": 0,
                }
            
            logger.info(f"Syncing {len(users)} users to node {node.address}")
            
            # Sync all users
            tasks = [self.sync_user_to_node(user.name, node) for user in users]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Count successes and failures
            valid_results = [r for r in results if isinstance(r, dict)]
            synced_count = sum(1 for r in valid_results if r.get("success"))
            failed_count = len(valid_results) - synced_count
            
            # Update node sync status
            if failed_count == 0:
                crud.update_node_sync_status(self.db, node.id, "synced")
            elif synced_count > 0:
                crud.update_node_sync_status(self.db, node.id, "pending")
            else:
                crud.update_node_sync_status(self.db, node.id, "failed")
            
            logger.info(
                f"Sync completed for node {node.address}: "
                f"{synced_count} succeeded, {failed_count} failed"
            )
            
            return {
                "node_id": node.id,
                "address": node.address,
                "total_users": len(users),
                "synced": synced_count,
                "failed": failed_count,
            }
            
        except Exception as e:
            logger.error(f"Error syncing users to node {node.address}: {e}")
            crud.update_node_sync_status(self.db, node.id, "failed")
            return {
                "node_id": node.id,
                "address": node.address,
                "error": str(e),
            }

    async def sync_all_nodes(self) -> List[dict]:
        """Sync all users to all healthy nodes.
        
        Returns:
            List of sync results for each node
        """
        # Get only healthy nodes
        nodes = crud.get_healthy_nodes(self.db)
        
        if not nodes:
            logger.warning("No healthy nodes available for sync")
            return []
        
        logger.info(f"Starting full sync for {len(nodes)} healthy nodes")
        
        # Sync all nodes concurrently
        tasks = [self.sync_all_users_to_node(node) for node in nodes]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        valid_results = [r for r in results if isinstance(r, dict)]
        
        total_synced = sum(r.get("synced", 0) for r in valid_results)
        total_failed = sum(r.get("failed", 0) for r in valid_results)
        
        logger.info(
            f"Full sync completed: {total_synced} users synced, "
            f"{total_failed} failed across {len(valid_results)} nodes"
        )
        
        return valid_results

    async def sync_pending_nodes(self) -> List[dict]:
        """Sync only nodes that have pending sync status.
        
        Returns:
            List of sync results for pending nodes
        """
        nodes = crud.get_nodes_needing_sync(self.db)
        
        if not nodes:
            logger.info("No nodes need sync")
            return []
        
        logger.info(f"Syncing {len(nodes)} nodes with pending status")
        
        tasks = [self.sync_all_users_to_node(node) for node in nodes]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        valid_results = [r for r in results if isinstance(r, dict)]
        
        logger.info(f"Pending sync completed for {len(valid_results)} nodes")
        
        return valid_results

    async def sync_user_to_all_nodes(self, user_name: str) -> List[dict]:
        """Sync a single user to all healthy nodes.
        
        Args:
            user_name: Name of the user to sync
            
        Returns:
            List of sync results
        """
        nodes = crud.get_healthy_nodes(self.db)
        
        if not nodes:
            logger.warning(f"No healthy nodes to sync user '{user_name}'")
            return []
        
        logger.info(f"Syncing user '{user_name}' to {len(nodes)} healthy nodes")
        
        tasks = [self.sync_user_to_node(user_name, node) for node in nodes]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        valid_results = [r for r in results if isinstance(r, dict)]
        success_count = sum(1 for r in valid_results if r.get("success"))
        
        logger.info(
            f"User '{user_name}' synced to {success_count}/{len(valid_results)} nodes"
        )
        
        return valid_results

    async def delete_user_from_all_nodes(self, user_name: str) -> List[dict]:
        """Delete a user from all nodes.
        
        Args:
            user_name: Name of the user to delete
            
        Returns:
            List of deletion results
        """
        nodes = crud.get_all_nodes(self.db)
        
        if not nodes:
            return []
        
        logger.info(f"Deleting user '{user_name}' from {len(nodes)} nodes")
        
        results = []
        for node in nodes:
            try:
                node_request = NodeRequests(
                    address=node.address,
                    port=node.port,
                    api_key=node.key,
                    timeout=10,
                    max_retries=2,
                )
                
                user_name_with_node = f"{user_name}-{node.name}"
                success = node_request.delete_user(user_name_with_node)
                
                results.append({
                    "node_id": node.id,
                    "address": node.address,
                    "user": user_name,
                    "success": success,
                })
                
            except Exception as e:
                logger.error(
                    f"Error deleting user '{user_name}' from node {node.address}: {e}"
                )
                results.append({
                    "node_id": node.id,
                    "address": node.address,
                    "user": user_name,
                    "success": False,
                    "error": str(e),
                })
        
        success_count = sum(1 for r in results if r.get("success"))
        logger.info(
            f"User '{user_name}' deleted from {success_count}/{len(results)} nodes"
        )
        
        return results
