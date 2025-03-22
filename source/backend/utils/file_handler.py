import os
import shutil
from fastapi import UploadFile
import uuid

UPLOAD_DIR = "uploads"

async def save_uploaded_file(uploaded_file: UploadFile) -> str:
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{uploaded_file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(uploaded_file.file, buffer)
    return file_path
