from fastapi import FastAPI
from contextlib import asynccontextmanager
from routers import wabot, payment, auth
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from starlette.middleware.cors import CORSMiddleware
from config import CONFIG
from database.models.adminuser import AdminUserDocument
from database.models.wabot import WaBotDocument

@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore
    """Initialize application services."""
    app.db = AsyncIOMotorClient(CONFIG.mongo_uri).wabot  # type: ignore[attr-defined]
    await init_beanie(app.db, document_models=[
        AdminUserDocument,
        WaBotDocument
    ])  # type: ignore[arg-type,attr-defined]
    print("Startup complete")
    yield
    print("Shutdown complete")

app = FastAPI(
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)