from typing import Dict, Any
from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException, status

from app.database import DatabaseManager
from app.models.organization import Organization
from app.models.admin import Admin
from app.utils.security import hash_password


class OrganizationService:
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.master_db = db.get_master_db()
        self.org_collection = self.master_db["organizations"]
        self.admin_collection = self.master_db["admins"]
    
    def create_organization(
        self,
        organization_name: str,
        email: str,
        password: str
    ) -> Dict[str, Any]:
        existing_org = self.org_collection.find_one(
            {"organization_name": organization_name}
        )
        
        if existing_org:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Organization '{organization_name}' already exists"
            )
        
        existing_admin = self.admin_collection.find_one({"email": email})
        if existing_admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Admin with email '{email}' already exists"
            )
        
        try:
            collection_name = self.db.create_organization_collection(organization_name)
            
            hashed_pwd = hash_password(password)
            admin = Admin(
                email=email,
                hashed_password=hashed_pwd,
                organization_name=organization_name,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                is_active=True
            )
            
            admin_result = self.admin_collection.insert_one(admin.to_dict())
            admin_id = str(admin_result.inserted_id)
            
            organization = Organization(
                organization_name=organization_name,
                collection_name=collection_name,
                admin_email=email,
                admin_id=admin_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                is_active=True
            )
            
            org_result = self.org_collection.insert_one(organization.to_dict())
            org_id = str(org_result.inserted_id)
            
            self.admin_collection.update_one(
                {"_id": ObjectId(admin_id)},
                {"$set": {"organization_id": org_id}}
            )
            
            return {
                "id": org_id,
                "organization_name": organization_name,
                "collection_name": collection_name,
                "admin_email": email,
                "admin_id": admin_id,
                "created_at": organization.created_at,
                "updated_at": organization.updated_at,
                "is_active": organization.is_active
            }
            
        except Exception as e:
            if 'collection_name' in locals():
                self.db.delete_organization_collection(collection_name)
            if 'admin_id' in locals():
                self.admin_collection.delete_one({"_id": ObjectId(admin_id)})
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create organization: {str(e)}"
            )
    
    def get_organization(self, organization_name: str) -> Dict[str, Any]:
        org = self.org_collection.find_one(
            {"organization_name": organization_name}
        )
        
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Organization '{organization_name}' not found"
            )
        
        org["id"] = str(org["_id"])
        del org["_id"]
        
        return org
    
    def update_organization(
        self,
        organization_name: str,
        new_email: str,
        new_password: str,
        current_admin_id: str
    ) -> Dict[str, Any]:
        org = self.org_collection.find_one(
            {"organization_name": organization_name}
        )
        
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Organization '{organization_name}' not found"
            )
        
        if str(org.get("admin_id")) != current_admin_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this organization"
            )
        
        try:
            existing_admin = self.admin_collection.find_one({
                "email": new_email,
                "_id": {"$ne": ObjectId(current_admin_id)}
            })
            
            if existing_admin:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Email '{new_email}' is already in use"
                )
            
            hashed_pwd = hash_password(new_password)
            self.admin_collection.update_one(
                {"_id": ObjectId(current_admin_id)},
                {
                    "$set": {
                        "email": new_email,
                        "hashed_password": hashed_pwd,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            self.org_collection.update_one(
                {"_id": org["_id"]},
                {
                    "$set": {
                        "admin_email": new_email,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            updated_org = self.org_collection.find_one({"_id": org["_id"]})
            updated_org["id"] = str(updated_org["_id"])
            del updated_org["_id"]
            
            return updated_org
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update organization: {str(e)}"
            )
    
    def delete_organization(
        self,
        organization_name: str,
        current_admin_id: str
    ) -> Dict[str, str]:
        org = self.org_collection.find_one(
            {"organization_name": organization_name}
        )
        
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Organization '{organization_name}' not found"
            )
        
        if str(org.get("admin_id")) != current_admin_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this organization"
            )
        
        try:
            collection_name = org.get("collection_name")
            if collection_name:
                self.db.delete_organization_collection(collection_name)
            
            admin_id = org.get("admin_id")
            if admin_id:
                self.admin_collection.delete_one({"_id": ObjectId(admin_id)})
            
            self.org_collection.delete_one({"_id": org["_id"]})
            
            return {
                "message": f"Organization '{organization_name}' deleted successfully"
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete organization: {str(e)}"
            )
