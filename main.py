from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import pandas as pd
from io import StringIO, BytesIO
import os, shutil, uuid
from datetime import datetime
from typing import Dict
import re

app = FastAPI()

# 파일 크기 제한 상수 (10MB)
MAX_FILE_SIZE = 10 * 1024 *1024
CHUNK_SIZE = 64* 1024

# 업로드된 파일 메타데이터 저장소
uploaded_files: Dict[str, dict] = {}

@app.post("/upload-file/")
async def upload_file(file: UploadFile = File(...)):
    # 파일 크기 검증
    file.size = 0
    file.file.seek(0, 2)    # 파일 끝으로 이동
    file_size = file.file.tell()
    file.file.seek(0)       # 포인터 초기화

    # 파일 너무 크면 반려
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"파일 크기 제한 초과 ({MAX_FILE_SIZE//1024//1024}MB)"
        )

    # 청크 단위로 파일 읽기
    contents = b''
    while True:
        chunk = await file.read(CHUNK_SIZE)
        if not chunk:
            break
        contents += chunk
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(413, "파일 크기 초과")
    
    # 파일 확장자 검증
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

    # 저장
    file_id = str(uuid.uuid4())
    upload_dir = os.path.abspath("uploads")
    os.makedirs(upload_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    MAX_FILENAME_LENGTH = 255
    # 기본 경로 제거
    sanitized_name = os.path.basename(file.filename)
    # 특수문자 변환
    sanitized_name = re.sub(r'[<>:"|?*]', '_', sanitized_name)
    # 제어문제 제거
    sanitized_name = re.sub(r'[\x00-\x1f]', '', sanitized_name)
    # 윈도우 예약어 처리
    windows_reserved = (['CON', 'PRN', 'AUX', 'NULL'] + 
                        [f'COM{i}' for i in range(1, 10)] + 
                        [f'LPT{i}' for i in range(1, 10)])
    if sanitized_name.upper().split('.')[0] in windows_reserved:
        sanitized_name = f"file_{sanitized_name}"

    if len(sanitized_name) > MAX_FILENAME_LENGTH:
        raise HTTPException(400, f"파일명이 너무 깁니다 (최대 {MAX_FILENAME_LENGTH}자)")
    
    safe_name = f"{file_id}_{timestamp}_{sanitized_name }"
    
    path = os.path.join(upload_dir, safe_name)

    final_path = os.path.abspath(path)
    if not final_path.startswith(upload_dir):
        raise HTTPException(400, "Inbalid file path detected ")
    
    # contents를 직접 기록(파일 포인터 리셋 불필요)
    with open(path, "wb") as buf:
        buf.write(contents)

    # 3. 메타데이터 저장
    uploaded_files[file_id] = {
        "path": path,
        "original_name": sanitized_name,
        "uploaded_at": datetime.now().isoformat()
    }

    # 4. 다운로드 URL 포함 응답
    return {
        "file_id": file_id,
        "original_filename": file.filename,
        "safe_filename" : sanitized_name,
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
