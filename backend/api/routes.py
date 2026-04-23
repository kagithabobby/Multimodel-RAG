import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from services.indexer import indexer
from services.retriever import retriever

router = APIRouter()

class QueryRequest(BaseModel):
    question: str

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    os.makedirs("data/uploads", exist_ok=True)
    file_path = f"data/uploads/{file.filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        indexer.ingest_pdf(file_path)
        return {"status": "success", "message": f"{file.filename} processed and indexed."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query")
async def query_system(request: QueryRequest):
    try:
        result = retriever.query(request.question)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
