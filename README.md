# Organization Management Service

A multi-tenant backend service built with FastAPI and MongoDB for managing organizations with dynamic collections. Each organization gets its own dedicated MongoDB collection, and the system uses a master database to store organization metadata and admin credentials.

## GitHub Repository

https://github.com/khushi-upadhyay/backend-organization-management-system.git

## Architecture

```
┌─────────────────────────────────────────┐
│           API Layer (Routes)            │
│     FastAPI endpoints and validation    │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│        Service Layer (Business Logic)   │
│   OrganizationService, AuthService      │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│      Database Layer (Data Access)       │
│   DatabaseManager, MongoDB Collections  │
└─────────────────────────────────────────┘
```

### High-Level Architecture Diagram

```
                    Client Application
                           │
                           ▼
                    ┌──────────────┐
                    │  FastAPI App │
                    │   (Routes)   │
                    └──────┬───────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Organization │  │   Admin      │  │   Health     │
│   Routes     │  │   Routes     │  │   Routes     │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       └─────────────────┼─────────────────┘
                         │
                         ▼
                    ┌──────────────┐
                    │   Services   │
                    │   (Classes)  │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   Database   │
                    │   Manager    │
                    └──────┬───────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Master DB   │  │   Org Coll   │  │   Org Coll   │
│ - orgs       │  │   org_abc    │  │   org_xyz    │
│ - admins     │  │              │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
```

## Design Choices

The application uses a modular, class-based architecture with clear separation between routes, services, and database layers. Service classes (`OrganizationService`, `AuthService`) encapsulate business logic, while a singleton `DatabaseManager` handles all MongoDB operations. The multi-tenant design uses a master database for organization metadata and creates dynamic collections per organization for data isolation. Security is implemented through bcrypt password hashing, JWT authentication with organization context, and authorization checks ensuring admins can only manage their own organization. Pydantic models provide type-safe input validation throughout the application.

## Prerequisites

- Python 3.9 or higher
- MongoDB 4.4+ (local or MongoDB Atlas)
- pip

## Installation

1. Clone the repository:
```bash
git clone https://github.com/khushi-upadhyay/backend-organization-management-system.git
cd backend-organization-management-system
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Initialize database schemas:
```bash
python scripts/init_db.py
```

## How to Run

Start the application:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

Access API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

- `POST /org/create` - Create a new organization
- `GET /org/get?organization_name=<name>` - Get organization details
- `PUT /org/update` - Update organization (requires authentication)
- `DELETE /org/delete?organization_name=<name>` - Delete organization (requires authentication)
- `POST /admin/login` - Admin login and get JWT token

## Testing

Run the test script:
```bash
python test_api.py
```
