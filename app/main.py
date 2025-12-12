from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager

from app.config import settings
from app.routes import organization_router, admin_router
from app.database import db_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"Starting {settings.APP_NAME}")
    print(f"Master Database: {settings.MASTER_DB_NAME}")
    print(f"JWT Expiration: {settings.ACCESS_TOKEN_EXPIRE_MINUTES} minutes")
    
    yield
    
    print("Shutting down application")
    db_manager.close()


app = FastAPI(
    title=settings.APP_NAME,
    description="Multi-tenant backend service for managing organizations with dynamic collections.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(organization_router)
app.include_router(admin_router)


@app.get("/", tags=["Health"])
async def root():
    return RedirectResponse(url="/docs")


@app.get("/health", tags=["Health"])
async def health_check():
    try:
        db_manager.get_master_db().command('ping')
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "database": db_status,
        "app": settings.APP_NAME
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
