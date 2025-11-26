"""
Custom FastAPI routes for vacation planner
Adds file download endpoint
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
import os

def add_custom_routes(app: FastAPI):
    """Add custom routes to the FastAPI app"""

    # Get the project root directory
    project_root = Path(__file__).parent.parent.parent
    outputs_dir = project_root / "outputs"

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

    @app.get("/downloads/list")
    async def list_downloads():
        """List all available vacation plan downloads"""
        if not outputs_dir.exists():
            return {"files": []}

        files = []
        for file in outputs_dir.glob("vacation_plan_*.docx"):
            stat = file.stat()
            files.append({
                "filename": file.name,
                "size": stat.st_size,
                "created": stat.st_ctime,
                "download_url": f"/download/{file.name}"
            })

        # Sort by creation time (newest first)
        files.sort(key=lambda x: x["created"], reverse=True)

        return {"files": files}
