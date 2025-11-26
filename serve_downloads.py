#!/usr/bin/env python3
"""
Simple download server for vacation plan documents
Runs alongside ADK web server to serve downloadable files
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import uvicorn

app = FastAPI(title="Vacation Plan Downloads")

# Enable CORS so ADK web UI can access downloads
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get outputs directory
outputs_dir = Path(__file__).parent / "outputs"
outputs_dir.mkdir(exist_ok=True)


@app.get("/")
async def root():
    """API information"""
    return {
        "service": "Vacation Plan Download Server",
        "version": "1.0.0",
        "endpoints": {
            "download": "/download/{filename}",
            "list": "/list"
        }
    }


@app.get("/download/{filename}")
async def download_file(filename: str):
    """
    Download vacation plan document

    Args:
        filename: Name of the file to download (must be .docx)

    Returns:
        FileResponse with the Word document
    """
    # Security: Only allow .docx files
    if not filename.endswith('.docx'):
        raise HTTPException(status_code=400, detail="Only .docx files can be downloaded")

    # Security: Prevent path traversal
    if '..' in filename or '/' in filename or '\\' in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    file_path = outputs_dir / filename

    # Check if file exists
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {filename}")

    # Return the file
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@app.get("/list")
async def list_downloads():
    """List all available vacation plan downloads"""
    files = []
    for file in outputs_dir.glob("vacation_plan_*.docx"):
        stat = file.stat()
        files.append({
            "filename": file.name,
            "size": stat.st_size,
            "size_mb": round(stat.st_size / 1024 / 1024, 2),
            "created": stat.st_ctime,
            "download_url": f"http://localhost:9000/download/{file.name}"
        })

    # Sort by creation time (newest first)
    files.sort(key=lambda x: x["created"], reverse=True)

    return {
        "count": len(files),
        "files": files
    }


if __name__ == "__main__":
    print("=" * 80)
    print("VACATION PLAN DOWNLOAD SERVER")
    print("=" * 80)
    print()
    print("Server running on: http://localhost:9000")
    print()
    print("Available endpoints:")
    print("  - GET  /             - API information")
    print("  - GET  /list         - List all vacation plans")
    print("  - GET  /download/{filename}  - Download a vacation plan")
    print()
    print(f"Serving files from: {outputs_dir.absolute()}")
    print()
    print("=" * 80)
    print()

    uvicorn.run(app, host="0.0.0.0", port=9000)
