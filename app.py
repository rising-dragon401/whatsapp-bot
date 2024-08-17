from fastapi import FastAPI
from contextlib import asynccontextmanager
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from starlette.middleware.cors import CORSMiddleware
from config import CONFIG
from database.models.adminuser import AdminUserDocument
from database.models.wabot import WaBotDocument
from middleware.jwtauth import JWTAuthMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.db = AsyncIOMotorClient(CONFIG.mongo_uri).wabot
    await init_beanie(app.db, document_models=[
        AdminUserDocument,
        WaBotDocument
    ])
    yield

app = FastAPI(
    lifespan=lifespan,
)

app.add_middleware(JWTAuthMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)