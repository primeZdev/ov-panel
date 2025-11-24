from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from backend.config import config
from backend.db.engine import get_db
from backend.db import crud
from backend.node.task import download_ovpn_client_from_node
from backend.node.requests import NodeRequests


templates = Jinja2Templates(directory="frontend/templates")
router = APIRouter(prefix=f"/{config.SUBSCRIPTION_PATH}", tags=["Subscription"])


@router.get("/{uuid}")
async def get_subscription(
    request: Request,
    uuid: str,
    db: Session = Depends(get_db),
):
    user = crud.get_user_by_uuid(db, uuid)
    if not user:
        raise HTTPException(status_code=404)
    nodes = crud.get_all_nodes(db)
    ovpn_download_links = {}
    for node in nodes:
        if not node.status:
            continue
        try:
            status = NodeRequests(
                address=node.address, port=node.port, api_key=node.key
            ).check_node()
        except Exception:
            continue
        if not status:
            continue
        link = await download_ovpn_client_from_node(user.name, node.address, db)
        if link:
            ovpn_download_links[node.name] = link

    return templates.TemplateResponse(
        "subscription.html",
        {
            "request": request,
            "name": user.name,
            "expiry_date": user.expiry_date,
            "is_active": user.is_active,
            "ovpn_download_links": ovpn_download_links,
        },
    )
