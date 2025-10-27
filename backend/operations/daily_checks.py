from backend.logger import logger
from backend.db import crud
from backend.db.engine import get_db
from .user_management import delete_user_on_server

import asyncio


async def check_user_expiry_date():
    """This function checks users' expiration dates"""
    db = next(get_db())

    try:
        expired_users = crud.get_expired_users(db)
        for user in expired_users:
            user.is_active = False
            await delete_user_on_server(user.name)
            await asyncio.sleep(2)  # to avoid overload the server with commands
        db.commit()

    except Exception as e:
        logger.error(f"Error in users expiration daily check -> {e}")
