from fastapi import APIRouter

from core.database import check_db_connection
from core.config import settings

router = APIRouter()


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "app": "HisaabAI",
        "environment": settings.ENVIRONMENT,
    }


@router.get("/health/db")
async def health_db():
    ok, detail = check_db_connection()
    return {
        "status": "ok" if ok else "error",
        "database": detail,
    }
