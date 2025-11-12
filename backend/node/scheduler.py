"""Background scheduler for automatic health checks and sync operations."""

import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from backend.logger import logger
from sqlalchemy.orm import Session
from backend.db.engine import sessionLocal
from backend.node.health_check import HealthCheckService
from backend.node.sync import SyncService


class BackgroundScheduler:
    """Background scheduler for health checks and sync operations."""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
    
    def get_db(self):
        """Get database session."""
        db = sessionLocal()
        try:
            return db
        finally:
            pass  # Don't close here, will be closed after job
    
    async def health_check_job(self):
        """Scheduled job to check health of all nodes."""
        db = self.get_db()
        try:
            logger.info("Running scheduled health check...")
            health_service = HealthCheckService(db)
            results = await health_service.check_all_nodes()
            
            healthy_count = sum(1 for r in results if r.get("is_healthy"))
            logger.info(
                f"Scheduled health check completed: "
                f"{healthy_count}/{len(results)} nodes healthy"
            )
            
            # Try to recover unhealthy nodes
            recovered = await health_service.auto_recover_nodes()
            if recovered:
                logger.info(f"Auto-recovered {len(recovered)} nodes")
                
        except Exception as e:
            logger.error(f"Error in health check job: {e}")
        finally:
            db.close()
    
    async def sync_pending_job(self):
        """Scheduled job to sync pending nodes."""
        db = self.get_db()
        try:
            logger.info("Running scheduled sync for pending nodes...")
            sync_service = SyncService(db)
            results = await sync_service.sync_pending_nodes()
            
            if results:
                total_synced = sum(r.get("synced", 0) for r in results)
                logger.info(
                    f"Scheduled sync completed: "
                    f"{total_synced} users synced to {len(results)} nodes"
                )
            else:
                logger.info("No pending nodes to sync")
                
        except Exception as e:
            logger.error(f"Error in sync pending job: {e}")
        finally:
            db.close()
    
    async def full_sync_job(self):
        """Scheduled job for full system sync (runs less frequently)."""
        db = self.get_db()
        try:
            logger.info("Running scheduled full system sync...")
            sync_service = SyncService(db)
            results = await sync_service.sync_all_nodes()
            
            total_synced = sum(r.get("synced", 0) for r in results)
            total_failed = sum(r.get("failed", 0) for r in results)
            
            logger.info(
                f"Full sync completed: {total_synced} users synced, "
                f"{total_failed} failed across {len(results)} nodes"
            )
            
        except Exception as e:
            logger.error(f"Error in full sync job: {e}")
        finally:
            db.close()
    
    def start(self):
        """Start the background scheduler."""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        try:
            # Health check every 10 seconds
            self.scheduler.add_job(
                self.health_check_job,
                trigger=IntervalTrigger(seconds=10),
                id="health_check",
                name="Health Check All Nodes",
                replace_existing=True,
            )
            
            # Sync pending nodes every 30 seconds
            self.scheduler.add_job(
                self.sync_pending_job,
                trigger=IntervalTrigger(seconds=30),
                id="sync_pending",
                name="Sync Pending Nodes",
                replace_existing=True,
            )
            
            # Full sync every 5 minutes
            self.scheduler.add_job(
                self.full_sync_job,
                trigger=IntervalTrigger(minutes=5),
                id="full_sync",
                name="Full System Sync",
                replace_existing=True,
            )
            
            self.scheduler.start()
            self.is_running = True
            logger.info("Background scheduler started successfully")
            logger.info("Jobs scheduled:")
            logger.info("  - Health check: every 10 seconds")
            logger.info("  - Sync pending: every 30 seconds")
            logger.info("  - Full sync: every 5 minutes")
            
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
            raise
    
    def stop(self):
        """Stop the background scheduler."""
        if not self.is_running:
            logger.warning("Scheduler is not running")
            return
        
        try:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Background scheduler stopped")
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")
            raise
    
    def get_jobs(self):
        """Get list of scheduled jobs."""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": str(job.next_run_time) if job.next_run_time else None,
            })
        return jobs


# Global scheduler instance
scheduler = BackgroundScheduler()
