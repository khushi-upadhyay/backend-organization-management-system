from fastapi import APIRouter, Depends, status
from typing import Dict, Any

from app.schemas.admin import AdminLogin, TokenResponse
from app.services.auth_service import AuthService
from app.database import DatabaseManager, get_db


router = APIRouter(prefix="/admin", tags=["Authentication"])


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Admin login",
    description="Authenticates an admin user and returns a JWT access token"
)
async def admin_login(
    credentials: AdminLogin,
    db: DatabaseManager = Depends(get_db)
) -> Dict[str, Any]:
    service = AuthService(db)
    result = service.authenticate_admin(
        email=credentials.email,
        password=credentials.password
    )
    return result
