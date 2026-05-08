import asyncio

from backend.logger import logger
from backend.db import crud
from backend.db.engine import get_db
from backend.node.task import change_user_status_on_all_nodes, get_users_used_traffic


async def enforce_user_limits():
    """Disable users who are expired or exceeded traffic"""
    db = next(get_db())

    try:
        expired_users = crud.get_expired_users(db)
        exceeded_users = crud.get_users_exceeded_traffic(db)

        users_to_disable = {u.id: u for u in expired_users + exceeded_users}.values()

        for user in users_to_disable:
            user.is_active = False
            await change_user_status_on_all_nodes(name=user.name, status=False, db=db)
            await asyncio.sleep(0.5)

        db.commit()

    except Exception as e:
        db.rollback()
        logger.error(f"Error in users expiration check -> {e}")

    finally:
        db.close()


async def check_user_used_traffic():
    db = next(get_db())
    nodes = crud.get_all_nodes(db)

    try:
        if nodes:
            for node in nodes:
                try:
                    users = await get_users_used_traffic(node, db=db)
                    logger.info(f"Traffic from node {node.address}: {users}")

                    if users:
                        all_users = {u.name: u for u in crud.get_all_users(db)}

                        for username, used_bytes in users.items():
                            clean_username = username.split("-")[0]

                            user = all_users.get(clean_username)
                            if user:
                                logger.info(
                                    f"User found: {clean_username}, old used: {user.used}, adding: {used_bytes}"
                                )
                                # Handle None value in used field
                                user.used = (user.used or 0) + used_bytes
                            else:
                                logger.warning(f"User not found: {clean_username}")

                except Exception as e:
                    db.rollback()
                    logger.error(
                        f"Error in users usage daily check -> {e}", exc_info=True
                    )

        db.commit()
        logger.info("Traffic update committed to database")

    except Exception as e:
        db.rollback()
        logger.error(f"Error in users usage daily check -> {e}", exc_info=True)

    finally:
        db.close()
