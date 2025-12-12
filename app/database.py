from pymongo import MongoClient
from pymongo.database import Database
from pymongo.server_api import ServerApi
from typing import Optional
from app.config import settings


class DatabaseManager:
    _instance: Optional['DatabaseManager'] = None
    _client: Optional[MongoClient] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            self._client = MongoClient(settings.MONGODB_URL, server_api=ServerApi('1'))
    
    @property
    def client(self) -> MongoClient:
        if self._client is None:
            self._client = MongoClient(settings.MONGODB_URL, server_api=ServerApi('1'))
        return self._client
    
    def get_master_db(self) -> Database:
        return self.client[settings.MASTER_DB_NAME]
    
    def get_organization_db(self, collection_name: str) -> Database:
        return self.client[settings.MASTER_DB_NAME]
    
    def create_organization_collection(self, org_name: str) -> str:
        collection_name = f"org_{org_name.lower().replace(' ', '_').replace('-', '_')}"
        db = self.get_master_db()
        collection = db[collection_name]
        dummy_id = collection.insert_one({"_type": "init"}).inserted_id
        collection.delete_one({"_id": dummy_id})
        return collection_name
    
    def delete_organization_collection(self, collection_name: str) -> bool:
        db = self.get_master_db()
        db[collection_name].drop()
        return True
    
    def collection_exists(self, collection_name: str) -> bool:
        db = self.get_master_db()
        return collection_name in db.list_collection_names()
    
    def migrate_collection(self, old_collection_name: str, new_collection_name: str) -> bool:
        db = self.get_master_db()
        
        if not self.collection_exists(old_collection_name):
            return False
        
        old_collection = db[old_collection_name]
        new_collection = db[new_collection_name]
        
        documents = list(old_collection.find())
        if documents:
            new_collection.insert_many(documents)
        
        old_collection.drop()
        return True
    
    def close(self):
        if self._client:
            self._client.close()
            self._client = None


db_manager = DatabaseManager()


def get_db() -> DatabaseManager:
    return db_manager
