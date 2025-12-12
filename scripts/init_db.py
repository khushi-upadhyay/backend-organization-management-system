#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import OperationFailure
from app.config import settings


def organizations_schema():
    return {
        "$jsonSchema": {
            "bsonType": "object",
            "required": [
                "organization_name",
                "collection_name",
                "admin_email",
                "admin_id",
                "created_at",
                "updated_at",
                "is_active"
            ],
            "properties": {
                "organization_name": {"bsonType": "string", "minLength": 1},
                "collection_name": {"bsonType": "string", "minLength": 1},
                "admin_email": {"bsonType": "string"},
                "admin_id": {"bsonType": ["string", "objectId"]},
                "created_at": {"bsonType": "date"},
                "updated_at": {"bsonType": "date"},
                "is_active": {"bsonType": "bool"}
            }
        }
    }


def admins_schema():
    return {
        "$jsonSchema": {
            "bsonType": "object",
            "required": [
                "email",
                "hashed_password",
                "organization_name",
                "created_at",
                "updated_at",
                "is_active"
            ],
            "properties": {
                "email": {"bsonType": "string"},
                "hashed_password": {"bsonType": "string"},
                "organization_name": {"bsonType": "string"},
                "organization_id": {"bsonType": ["string", "objectId"]},
                "created_at": {"bsonType": "date"},
                "updated_at": {"bsonType": "date"},
                "is_active": {"bsonType": "bool"}
            }
        }
    }


def org_collection_schema():
    return {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["_type"],
            "properties": {
                "_type": {"bsonType": "string"}
            }
        }
    }


def ensure_collection_with_validator(db, name, validator):
    if name in db.list_collection_names():
        try:
            db.command("collMod", name, validator=validator, validationLevel="strict", validationAction="error")
            print(f"Updated validator on '{name}'")
        except OperationFailure as e:
            print(f"Warning: collMod failed for '{name}': {e.details if hasattr(e, 'details') else e}")
    else:
        db.create_collection(name, validator=validator, validationLevel="strict")
        print(f"Created collection '{name}' with validator")


def sanitize_org_name(org_name: str) -> str:
    return f"org_{org_name.lower().replace(' ', '_').replace('-', '_')}"


def main():
    parser = argparse.ArgumentParser(description="Initialize MongoDB JSON Schema validators")
    parser.add_argument("--uri", default=settings.MONGODB_URL, help="MongoDB URI")
    parser.add_argument("--db", default=settings.MASTER_DB_NAME, help="Database name")
    parser.add_argument("--org", default=None, help="Organization name to (re)apply per-org validator")
    args = parser.parse_args()

    print(f"Connecting to MongoDB: {args.uri.split('@')[1] if '@' in args.uri else args.uri}")
    if "mongodb+srv://" in args.uri:
        client = MongoClient(args.uri, server_api=ServerApi('1'))
    else:
        client = MongoClient(args.uri)
    
    try:
        client.admin.command('ping')
        print("Successfully connected to MongoDB!")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        return
    
    db = client[args.db]
    print(f"Using database: {args.db}")

    ensure_collection_with_validator(db, "organizations", organizations_schema())
    ensure_collection_with_validator(db, "admins", admins_schema())

    if args.org:
        col_name = sanitize_org_name(args.org)
        ensure_collection_with_validator(db, col_name, org_collection_schema())
        print(f"Per-org collection ensured: {col_name}")

    print("MongoDB schema initialization complete.")


if __name__ == "__main__":
    main()
