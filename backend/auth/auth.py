from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import Optional, Union
from backend.db.engine import get_db
from backend.config import config
from backend.db import crud


ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(tags=["Login"])

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(db: Session, username: str, password: str):
    main_admin_username = config.ADMIN_USERNAME
    main_admin_password = config.ADMIN_PASSWORD
    if username == main_admin_username and password == main_admin_password:
        return {"username": username, "type": "main_admin"}

    admin = crud.it_is_admin(db, username=username)
    if admin:
        if verify_password(password, admin.password):
            return {"username": admin.username, "type": "admin"}

    return None


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(hours=24))
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, config.JWT_SECRET_KEY, algorithm=ALGORITHM)

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    admin = authenticate_user(db, form_data.username, form_data.password)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The username or password is incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(seconds=config.JWT_ACCESS_TOKEN_EXPIRES)
    access_token = create_access_token(
        data={"sub": admin["username"], "role": admin["type"]},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/{config.URLPATH}/login", auto_error=False)


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=[ALGORITHM])
  
        username: str = payload.get("sub")
        user_type: str = payload.get("type")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return {"username": username, "type": user_type}


# ==================== NEW API KEY AUTHENTICATION ====================

def verify_api_key(x_api_key: Optional[str] = Header(None, alias="X-API-Key")) -> dict:
    """
    Verify API key from X-API-Key header.
    This is for external integrations that need to access the API.
    
    Usage:
        Add header: X-API-Key: your-api-key-here
    
    Returns:
        dict with authentication info if valid
    
    Raises:
        HTTPException if API key is invalid or missing
    """
    if not config.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="API Key authentication is not configured on this server",
        )
    
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-API-Key header",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    if x_api_key != config.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    return {"type": "api_key", "authenticated": True}


def verify_jwt_or_api_key(
    token: Optional[str] = Depends(oauth2_scheme),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
) -> dict:
    """
    Accept either JWT Bearer token OR API Key authentication.
    This allows both frontend (JWT) and external integrations (API Key) to access endpoints.
    
    Priority:
        1. Try API Key first if present
        2. Fall back to JWT Bearer token
        3. Raise error if neither is valid
    
    Returns:
        dict with authentication info
    """
    # Try API Key first if provided
    if x_api_key:
        if not config.API_KEY:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="API Key authentication is not configured",
            )
        if x_api_key == config.API_KEY:
            return {"type": "api_key", "authenticated": True}
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API Key",
                headers={"WWW-Authenticate": "ApiKey"},
            )
    
    # Fall back to JWT token
    if token:
        try:
            payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            user_type: str = payload.get("type")
            if username:
                return {"username": username, "type": user_type, "authenticated": True}
        except JWTError:
            pass
    
    # Neither authentication method worked
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials. Provide either valid JWT Bearer token or X-API-Key header",
        headers={"WWW-Authenticate": "Bearer, ApiKey"},
    )

