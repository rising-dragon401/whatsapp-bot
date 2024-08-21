from fastapi import FastAPI
from config import CONFIG
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from database.models.adminusers import AdminUserDocument
from database.models.wabots import WaBotDocument
from database.models.botusers import BotUserDocument
from database.models.payments import PaymentDocument
from database.models.pdffiles import PdfFileDocument

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.db = AsyncIOMotorClient(CONFIG.mongo_uri).wabot
    await init_beanie(app.db, document_models=[
        AdminUserDocument,
        WaBotDocument,
        BotUserDocument,
        PaymentDocument,
        PdfFileDocument
    ])
    yield