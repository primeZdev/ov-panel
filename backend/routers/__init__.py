from auth.auth import router as login_router
from .users import router as user_router
from .admins import router as admin_router
from .node import router as node_router
from .setting import router as setting_router

all_routers = [
    login_router,
    user_router,
    setting_router,
    node_router,
    admin_router,
]
