import base64
from fastapi import APIRouter, HTTPException
from api.models.schemas import DocumentUploadRequest
from api.services.upload_service import ingest_document

router = APIRouter(tags=["Document Upload"])

@router.post("/upload")
@router.post("/api/upload")
def upload_document_endpoint(req: DocumentUploadRequest):
    try:
        content = req.content
        if "base64," in content:
            content = content.split("base64,")[1]
        
        try:
            content_bytes = base64.b64decode(content)
        except Exception:
            content_bytes = req.content.encode("utf-8")
            
        return ingest_document(req.file_name, content_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process document upload: {str(e)}")
