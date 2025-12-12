from typing import Dict, Any
from datetime import timedelta
from fastapi import HTTPException, status

from app.database import DatabaseManager
from app.utils.security import verify_password, create_access_token
from app.config import settings


class AuthService:
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.master_db = db.get_master_db()
        self.admin_collection = self.master_db["admins"]
        self.org_collection = self.master_db["organizations"]
    
    def authenticate_admin(self, email: str, password: str) -> Dict[str, Any]:
        admin = self.admin_collection.find_one({"email": email})
        
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not verify_password(password, admin.get("hashed_password", "")):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not admin.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin account is inactive"
            )
        
        org_id = admin.get("organization_id")
        org_name = admin.get("organization_name")
        
        admin_id = str(admin["_id"])
        token_data = {
            "sub": admin_id,
            "email": email,
            "organization_id": org_id,
            "organization_name": org_name
        }
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data=token_data,
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "admin_id": admin_id,
            "organization_id": org_id,
            "organization_name": org_name,
            "email": email
        }
