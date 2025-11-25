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

        ovpn_download_links[node.name] = (
            f"{request.base_url}{config.SUBSCRIPTION_PATH}/download/{uuid}/{node.name}"
        )

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


@router.get("/download/{uuid}/{node_name}")
async def download_ovpn(
    uuid: str,
    node_name: str,
    db: Session = Depends(get_db),
):
    user = crud.get_user_by_uuid(db, uuid)
    if not user:
        raise HTTPException(status_code=404)
    node_obj = crud.get_node_by_name(db, node_name)
    if not node_obj:
        raise HTTPException(status_code=404)
    response = await download_ovpn_client_from_node(user.name, node_obj.address, db)
    if not response:
        raise HTTPException(status_code=404, detail="File not found")
    return response
