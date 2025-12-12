from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class AdminLogin(BaseModel):
    email: EmailStr = Field(..., description="Admin email address")
    password: str = Field(..., description="Admin password")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "admin@testorg.com",
                "password": "SecurePass123!"
            }
        }


class AdminResponse(BaseModel):
    id: str = Field(..., description="Admin user ID")
    email: str = Field(..., description="Admin email address")
    organization_name: str = Field(..., description="Associated organization name")
    organization_id: Optional[str] = Field(None, description="Organization ID reference")
    created_at: datetime = Field(..., description="Creation timestamp")
    is_active: bool = Field(..., description="Whether the admin is active")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439012",
                "email": "admin@testorg.com",
                "organization_name": "Test Organization",
                "organization_id": "507f1f77bcf86cd799439011",
                "created_at": "2024-01-01T00:00:00",
                "is_active": True
            }
        }


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    admin_id: str = Field(..., description="Admin user ID")
    organization_id: str = Field(..., description="Organization ID")
    organization_name: str = Field(..., description="Organization name")
    email: str = Field(..., description="Admin email")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "admin_id": "507f1f77bcf86cd799439012",
                "organization_id": "507f1f77bcf86cd799439011",
                "organization_name": "Test Organization",
                "email": "admin@testorg.com"
            }
        }
