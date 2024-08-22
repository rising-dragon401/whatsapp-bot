from fastapi import APIRouter, HTTPException
import logging
from database.models.adminusers import (
    read_all_adminusers
)

router = APIRouter(
    prefix="/api/adminusers",
    tags=["adminusers"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.get("/")
async def getAllAdminUsers(admin_id: str, permission: str):
    adminusers = await read_all_adminusers(admin_id, permission)
    return adminusers