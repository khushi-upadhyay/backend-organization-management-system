from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)
    
    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")


class Organization(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    organization_name: str = Field(..., description="Unique organization name")
    collection_name: str = Field(..., description="MongoDB collection name for this org")
    admin_email: str = Field(..., description="Admin email address")
    admin_id: Optional[str] = Field(None, description="Reference to admin user ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }
    
    def to_dict(self) -> dict:
        data = self.model_dump(by_alias=True, exclude={"id"})
        if self.id:
            data["_id"] = self.id
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> "Organization":
        if "_id" in data:
            data["id"] = str(data["_id"])
        return cls(**data)
