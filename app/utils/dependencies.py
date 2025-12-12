from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any
from app.utils.security import decode_access_token
from app.database import get_db, DatabaseManager


security = HTTPBearer()


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: DatabaseManager = Depends(get_db)
) -> Dict[str, Any]:
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    admin_id = payload.get("sub")
    organization_id = payload.get("organization_id")
    organization_name = payload.get("organization_name")
    email = payload.get("email")
    
    if not admin_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    master_db = db.get_master_db()
    admin_collection = master_db["admins"]
    
    from bson import ObjectId
    admin = admin_collection.find_one({"_id": ObjectId(admin_id)})
    
    if not admin or not admin.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin user not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {
        "admin_id": admin_id,
        "organization_id": organization_id,
        "organization_name": organization_name,
        "email": email
    }
