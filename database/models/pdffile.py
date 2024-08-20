from pydantic import BaseModel, Field
from beanie import Document
from datetime import datetime
from typing import Optional

class PdfFile(BaseModel):
    name: str = Field(...)
    path: str = Field(...)
    size: int = Field(...)
    created_at: str = Field(...)

class PdfFileDocument(Document, PdfFile):
    class Settings:
        name = "pdffiles"

async def add_pdf_file(pdfFile: PdfFileDocument) -> PdfFileDocument:
    return await pdfFile.insert()

async def all_pdf_files() -> list[PdfFileDocument]:
    return await PdfFileDocument.find_all().to_list()

async def delete_pdf_file(id: str) -> str:
    pdffile = await PdfFileDocument.get(id)
    if pdffile:
        pathname = pdffile.path
        pdffile = await pdffile.delete()
        return pathname
    else:
        return ""