from pydantic import BaseModel, Field
from beanie import Document

class PdfFile(BaseModel):
    name: str = Field(...)
    path: str = Field(...)
    size: int = Field(...)
    created_at: str = Field(...)

class PdfFileDocument(Document, PdfFile):
    class Settings:
        name = "pdffiles"

async def read_all_pdffiles() -> list[PdfFileDocument]:
    return await PdfFileDocument.find_all().to_list()

async def create_pdffile(pdfFile: PdfFileDocument) -> PdfFileDocument:
    return await pdfFile.insert()

async def delete_pdffile(id: str) -> str:
    pdffile = await PdfFileDocument.get(id)
    if pdffile:
        pathname = pdffile.path
        pdffile = await pdffile.delete()
        return pathname
    else:
        return ""