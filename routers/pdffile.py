from fastapi import APIRouter, HTTPException
from starlette.requests import Request
import logging
from database.models.pdffile import (
    all_pdf_files,
    add_pdf_file,
    delete_pdf_file,
    PdfFileDocument,
    PdfFile,
)
import os
from embedding.embedding import (
    initate_indexs,
    embedding_pdf_file
)

router = APIRouter(
    prefix="/api/pdffile",
    tags=["pdffile"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.get("/")
async def read_pdf_files():
    pdffiles = await all_pdf_files()
    return pdffiles

@router.post("/", response_model=PdfFile)
async def create_new_pdffile(pdffile: PdfFile):
    pdffile_doc = PdfFileDocument(**pdffile.model_dump())
    return await add_pdf_file(pdffile_doc)

@router.delete("/{pdffile_id}", response_model=dict)
async def delete_pdffile(pdffile_id: str):
    filepath = await delete_pdf_file(pdffile_id)
    if len(filepath) > 0:
        if not os.path.isfile(filepath):
            raise HTTPException(status_code=404, detail="File not found")

        try:
            os.remove(filepath)
            return {"detail": "PDF File is deleted."}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")

    raise HTTPException(status_code=404, detail="PDF File is not found.")

@router.post("/embedding")
async def embedding_data():
    try:
        initate_indexs()
        pdfdocs = await all_pdf_files()
        for pdfdoc in pdfdocs:
            embedding_pdf_file(pdfdoc.path)
        return {"detaile": "Embedding is successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error embedding: {str(e)}")