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
            await change_user_status_on_all_nodes(uuid=user.uuid, name=user.name, status=False, db=db)
            await asyncio.sleep(0.5)

        db.commit()

    except Exception as e:
        db.rollback()
        logger.error(f"Error in users expiration check -> {e}")

    finally:
        db.close()


async def check_user_used_traffic():
    db = next(get_db())

    try:
        nodes = crud.get_all_nodes(db)

        if not nodes:
            logger.warning("No nodes found")
            return

        all_users = {u.name: u for u in crud.get_all_users(db)}

        for node in nodes:
            try:
                users = await get_users_used_traffic(node, db=db)

                if not users:
                    continue

                for username, used_bytes in users.items():
                    clean_username = username.split("-")[0]

                    user = all_users.get(clean_username)

                    if not user:
                        logger.warning(f"User not found: {clean_username}")
                        continue
                    
                    last_usage = user.last_node_usage or 0
                    total_used = user.used or 0

                    if used_bytes >= last_usage:
                        delta = used_bytes - last_usage

                    # counter reset / reconnect
                    else:
                        delta = used_bytes

                    user.used = total_used + delta
                    user.last_node_usage = used_bytes

                    logger.info(
                        f"[{clean_username}], last={last_usage}, current={used_bytes}, delta={delta} "

                    )

                # commit per node
                db.commit()

                logger.info(f"Traffic data committed for node {node.address}")

            except Exception as e:
                db.rollback()

                logger.error(
                    f"Error while processing node " f"{node.address} -> {e}",
                    exc_info=True,
                )

    except Exception as e:
        db.rollback()

        logger.error(f"Error in check_user_used_traffic -> {e}", exc_info=True)

    finally:
        db.close()
