"""
Download API - Serves generated trip documents for download
"""

from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

# Output directory where documents are stored
OUTPUT_DIR = Path(__file__).parent.parent.parent / "outputs"

router = APIRouter()


@router.get("/download/{filename}")
async def download_document(filename: str):
    """
    Download a generated trip document.

    Args:
        filename: Name of the file to download (e.g., paris_20251215_120000.docx)

    Returns:
        FileResponse with the document
    """
    # Security: Only allow .docx files from outputs directory
    if not filename.endswith('.docx'):
        raise HTTPException(status_code=400, detail="Only .docx files can be downloaded")

    # Prevent directory traversal attacks
    if '..' in filename or '/' in filename or '\\' in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    file_path = OUTPUT_DIR / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Document not found")

    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


@router.get("/documents")
async def list_documents():
    """
    List all available trip documents.

    Returns:
        List of document filenames with metadata
    """
    if not OUTPUT_DIR.exists():
        return {"documents": []}

    documents = []
    for file_path in OUTPUT_DIR.glob("*.docx"):
        documents.append({
            "filename": file_path.name,
            "download_url": f"/download/{file_path.name}",
            "size_bytes": file_path.stat().st_size,
            "created_at": file_path.stat().st_mtime
        })

    # Sort by creation time (newest first)
    documents.sort(key=lambda x: x["created_at"], reverse=True)

    return {"documents": documents}
