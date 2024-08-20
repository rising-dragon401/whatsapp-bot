from fastapi import FastAPI
from config import CONFIG
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from database.models.adminuser import AdminUserDocument
from database.models.wabot import WaBotDocument
from database.models.user import UserDocument
from database.models.payment import PaymentDocument
from database.models.pdffile import PdfFileDocument

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.db = AsyncIOMotorClient(CONFIG.mongo_uri).wabot
    await init_beanie(app.db, document_models=[
        AdminUserDocument,
        WaBotDocument,
        UserDocument,
        PaymentDocument,
        PdfFileDocument
    ])
    yield