from fastapi import APIRouter, Depends, status
from typing import Dict, Any

from app.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse
)
from app.services.organization_service import OrganizationService
from app.database import DatabaseManager, get_db
from app.utils.dependencies import get_current_admin


router = APIRouter(prefix="/org", tags=["Organizations"])


@router.post(
    "/create",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new organization",
    description="Creates a new organization with a dedicated collection and an admin user"
)
async def create_organization(
    org_data: OrganizationCreate,
    db: DatabaseManager = Depends(get_db)
) -> Dict[str, Any]:
    service = OrganizationService(db)
    result = service.create_organization(
        organization_name=org_data.organization_name,
        email=org_data.email,
        password=org_data.password
    )
    return result


@router.get(
    "/get",
    response_model=OrganizationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get organization details",
    description="Retrieves organization details by name from the master database"
)
async def get_organization(
    organization_name: str,
    db: DatabaseManager = Depends(get_db)
) -> Dict[str, Any]:
    service = OrganizationService(db)
    result = service.get_organization(organization_name)
    return result


@router.put(
    "/update",
    response_model=OrganizationResponse,
    status_code=status.HTTP_200_OK,
    summary="Update organization",
    description="Updates organization admin credentials (requires authentication)"
)
async def update_organization(
    org_data: OrganizationUpdate,
    db: DatabaseManager = Depends(get_db),
    current_admin: Dict[str, Any] = Depends(get_current_admin)
) -> Dict[str, Any]:
    service = OrganizationService(db)
    result = service.update_organization(
        organization_name=org_data.organization_name,
        new_email=org_data.email,
        new_password=org_data.password,
        current_admin_id=current_admin["admin_id"]
    )
    return result


@router.delete(
    "/delete",
    status_code=status.HTTP_200_OK,
    summary="Delete organization",
    description="Deletes an organization and all its associated data (requires authentication)"
)
async def delete_organization(
    organization_name: str,
    db: DatabaseManager = Depends(get_db),
    current_admin: Dict[str, Any] = Depends(get_current_admin)
) -> Dict[str, str]:
    service = OrganizationService(db)
    result = service.delete_organization(
        organization_name=organization_name,
        current_admin_id=current_admin["admin_id"]
    )
    return result
