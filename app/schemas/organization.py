from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime


class OrganizationCreate(BaseModel):
    organization_name: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Unique name for the organization"
    )
    email: EmailStr = Field(..., description="Admin email address")
    password: str = Field(
        ...,
        min_length=8,
        description="Admin password (minimum 8 characters)"
    )
    
    @validator('organization_name')
    def validate_org_name(cls, v):
        if not v.replace(' ', '').replace('-', '').replace('_', '').isalnum():
            raise ValueError('Organization name must contain only alphanumeric characters, spaces, hyphens, or underscores')
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "organization_name": "Test Organization",
                "email": "admin@testorg.com",
                "password": "SecurePass123!"
            }
        }


class OrganizationUpdate(BaseModel):
    organization_name: str = Field(
        ...,
        description="Current organization name to update"
    )
    email: EmailStr = Field(..., description="New admin email address")
    password: str = Field(
        ...,
        min_length=8,
        description="New admin password"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "organization_name": "Test Organization",
                "email": "newadmin@testorg.com",
                "password": "NewSecurePass123!"
            }
        }


class OrganizationQuery(BaseModel):
    organization_name: str = Field(..., description="Organization name to query")
    
    class Config:
        json_schema_extra = {
            "example": {
                "organization_name": "Test Organization"
            }
        }


class OrganizationResponse(BaseModel):
    id: str = Field(..., description="Organization ID")
    organization_name: str = Field(..., description="Organization name")
    collection_name: str = Field(..., description="MongoDB collection name")
    admin_email: str = Field(..., description="Admin email address")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    is_active: bool = Field(..., description="Whether the organization is active")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "organization_name": "Test Organization",
                "collection_name": "org_test_organization",
                "admin_email": "admin@testorg.com",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
                "is_active": True
            }
        }
