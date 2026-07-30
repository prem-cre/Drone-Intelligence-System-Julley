from fastapi import APIRouter, HTTPException
from api.models.schemas import DocumentUploadRequest
from api.services.upload_service import ingest_document

router = APIRouter(tags=["Document Upload"])

@router.post("/upload")
@router.post("/api/upload")
def upload_document_endpoint(req: DocumentUploadRequest):
    try:
        content_bytes = req.content.encode("utf-8")
        return ingest_document(req.file_name, content_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process document upload: {str(e)}")
