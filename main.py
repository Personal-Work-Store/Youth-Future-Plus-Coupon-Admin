from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import pandas as pd
from io import StringIO, BytesIO
import os, shutil, uuid
from datetime import datetime
from typing import Dict

app = FastAPI()

# 업로드된 파일 메타데이터 저장소
uploaded_files: Dict[str, dict] = {}

@app.post("/upload-file/")
async def upload_file(file: UploadFile = File(...)):
    # 1. 파일 파싱 & 검증 (기존 로직)
    contents = await file.read()
    ext = file.filename.split(".")[-1].lower()

    try:
        if ext == "csv":
            df = pd.read_csv(StringIO(contents.decode("utf-8")))
        elif ext in ("xlsx", "xls"):
            df = pd.read_excel(BytesIO(contents))
        else:
            raise HTTPException(400, "지원되지 않는 파일 형식입니다.")
    except pd.errors.EmptyDataError:
        raise HTTPException(400, "파일에 읽을 수 있는 데이터가 없습니다.")

    if df.empty:
        raise HTTPException(400, "파일에 데이터가 없습니다.")
    if len(df.columns) != 1 or df.columns[0] != "customer_id":
        raise HTTPException(400, "헤더가 customer_id 하나만 있어야 합니다.")
    if len(df) == 0:
        raise HTTPException(400, "회원 목록이 비어있습니다.")

    # 2. 저장
    file_id = str(uuid.uuid4())
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = f"{file_id}_{timestamp}_{file.filename}"
    path = os.path.join(upload_dir, safe_name)
    
    # contents를 직접 기록(파일 포인터 리셋 불필요)
    with open(path, "wb") as buf:
        buf.write(contents)

    # 3. 메타데이터 저장
    uploaded_files[file_id] = {
        "path": path,
        "original_name": file.filename,
        "uploaded_at": datetime.now().isoformat()
    }

    # 4. 다운로드 URL 포함 응답
    return {
        "file_id": file_id,
        "filename": file.filename,
        "download_url": f"/download/{file_id}"
    }

@app.get("/download/{file_id}")
async def download_file(file_id: str):
    # file_id 만으로 접근 허용
    info = uploaded_files.get(file_id)
    if not info:
        raise HTTPException(404, "파일을 찾을 수 없습니다.")
    if not os.path.exists(info["path"]):
        raise HTTPException(404, "서버에 파일이 없습니다.")
    
    # 파일 그대로 내려주기
    return FileResponse(
        path=info["path"],
        filename=info["original_name"],
        media_type="application/octet-stream"
    )
