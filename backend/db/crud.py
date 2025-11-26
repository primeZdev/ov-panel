from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime
from uuid import uuid4

from backend.logger import logger
from backend.schema._input import CreateUser, UpdateUser, NodeCreate
from .models import User, Admin, Node, Settings


def get_all_users(db: Session):
    users = db.query(User).all()
    return users


def get_user_by_name(db: Session, name: str):
    user = db.query(User).filter(User.name == name).first()
    if user:
        return user
    return None


def get_user_by_uuid(db: Session, uuid: str):
    user = db.query(User).filter(User.uuid == uuid).first()
    if user:
        return user
    return None


def create_user(db: Session, request: CreateUser, owner: str):
    username = request.name.replace(" ", "_")

    if db.query(User).filter(User.name == username).first():
        raise HTTPException(
            status_code=400, detail="user with this name already exists"
        )

    new_user = User(
        name=username, expiry_date=request.expiry_date, owner=owner, uuid=str(uuid4())
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info(f"user created successfully: {request.name}")
    return new_user


def update_user(db: Session, uuid: str, request: UpdateUser):
    user = db.query(User).filter(User.uuid == uuid).first()
    if not user:
        raise HTTPException(status_code=404, detail="user not found on database")

    if request.expiry_date >= datetime.today().date():
        user.is_active = True
    else:
        user.is_active = False
    user.expiry_date = request.expiry_date

    db.commit()
    db.refresh(user)
    return {"detail": "User updated successfully"}


def change_user_status(db: Session, uuid: str, status: bool) -> bool:
    try:
        user = db.query(User).filter(User.uuid == uuid).first()
        user.is_active = status
        db.commit()
        db.refresh(user)
        return True
    except Exception as e:
        logger.error(f"Error when change status for user:{user.name} on db: {e}")
        return False


def get_expired_users(db: Session):
    return (
        db.query(User)
        .filter(User.expiry_date < datetime.now(), User.is_active == True)
        .all()
    )


def delete_user(db: Session, name: str):
    user = db.query(User).filter(User.name == name).first()
    if not user:
        raise HTTPException(status_code=404, detail="user not found on database")

    db.delete(user)
    db.commit()


# admins crud
def get_all_admins(db: Session):
    admins = db.query(Admin).all()
    return admins


def it_is_admin(db: Session, username: str):
    admin = db.query(Admin).filter(Admin.username == username).first()
    if not admin:
        return False
    return admin


# nodes crud
def get_all_nodes(db: Session):
    nodes = db.query(Node).all()
    return nodes


def get_node_by_address(db: Session, address: str):
    return db.query(Node).filter(Node.address == address).first()


def get_node_by_id(db: Session, id: int):
    return db.query(Node).filter(Node.id == id).first()


def get_node_by_name(db: Session, name: str):
    return db.query(Node).filter(Node.name == name).first()


def create_node(db: Session, request: NodeCreate):
    new_node = Node(
        name=request.name,
        address=request.address,
        tunnel_address=request.tunnel_address,
        ovpn_port=request.ovpn_port,
        protocol=request.protocol,
        port=request.port,
        key=request.key,
        status=request.status,
    )

    db.add(new_node)
    db.commit()
    db.refresh(new_node)
    return new_node


def update_node(db: Session, node_id: int, request: NodeCreate):
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    node.name = request.name
    node.tunnel_address = request.tunnel_address
    node.ovpn_port = request.ovpn_port
    node.protocol = request.protocol
    node.port = request.port
    node.key = request.key
    node.status = request.status
    db.commit()
    db.refresh(node)
    return node


def delete_node(db: Session, id: int):
    node = db.query(Node).filter(Node.id == id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    db.delete(node)
    db.commit()
    return {"detail": "Node deleted successfully"}


# settings crud
def get_settings(db: Session):
    settings = db.query(Settings).first()
    if not settings:
        settings = Settings(port=1194)
        settings.protocol = "tcp"
        db.add(settings)
        db.commit()
        db.refresh(settings)

    return settings
