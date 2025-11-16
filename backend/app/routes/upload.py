from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List

router = APIRouter()


@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    """Basic file upload endpoint - placeholder for now"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    return {
        "message": "File upload endpoint - to be implemented",
        "filename": file.filename,
        "content_type": file.content_type,
        "size": 0  # Will be implemented later
    }


@router.get("/")
async def list_uploads():
    """List uploaded files - placeholder for now"""
    return {
        "message": "List uploads - to be implemented",
        "files": []
    }

