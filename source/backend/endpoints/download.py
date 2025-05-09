from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, FileResponse
import os

router = APIRouter()

# POST endpoint that returns a download link as JSON
@router.post("/download_weights")
async def get_download_link(request: Request):
    body = await request.json()
    weights_path = body.get("weights_path")
    if not weights_path:
        raise HTTPException(status_code=400, detail="weights_path not provided")
    if not os.path.exists(weights_path):
        raise HTTPException(status_code=404, detail="File not found")
    # Construct the URL for the GET endpoint that serves the file.
    # Adjust the host/port as needed.
    download_link = f"https://llm-garage-api-513913820596.us-central1.run.app/download/download_file?weights_path={weights_path}"
    
    return JSONResponse({"download_link": download_link})

# GET endpoint that serves the file for download
@router.get("/download_file")
async def download_file_get(weights_path: str):
    if not os.path.exists(weights_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(
        path=weights_path, 
        media_type="application/octet-stream", 
        filename=os.path.basename(weights_path)
    )
