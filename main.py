from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import pandas as pd
from io import StringIO, BytesIO
import os, shutil, uuid
from datetime import datetime
from typing import Dict
import re

app = FastAPI()

# 파일 크기 제한 상수 (10MB) Dos 공격 방지
MAX_FILE_SIZE = 10 * 1024 * 1024
# 청크 크게 제한 상수 (64KB) 메모리 효율성 확보 메모리 오버플로우 방지 및 시스템 안정성 확보
CHUNK_SIZE = 64 * 1024
# 업로드된 파일 메타데이터 저장소
uploaded_files: Dict[str, dict] = {}


# 파일 크기 검증
def validate_file_size(file: UploadFile) -> int:
    file_size = 0  # 변수 초기화
    file.file.seek(0, 2)  # 포인터 끝으로 이동
    file_size = file.file.tell()  # 실제 파일 사이즈 대입
    file.file.seek(0)  # 포인터 초기화

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"파일 크기 제한 초과 ({MAX_FILE_SIZE//1024//1024}MB)",
        )
    return file_size


# 청크 단위로 파일 읽기
async def read_file_in_chunks(file: UploadFile) -> bytes:
    contents = b""
    while True:
        chunk = await file.read(CHUNK_SIZE)
        if not chunk:
            break
        contents += chunk
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(413, "파일 크기 초과")
    return contents


# 파일 형식 및 데이터 검증
def validate_file_format_and_data(filename: str, contents: bytes) -> pd.DataFrame:
    # 파일 명에서 확장자 추출
    ext = filename.split(".")[-1].lower()
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

    return df


# 파일명 정제
def sanitize_filename(filename: str) -> str:
    # 기본 경로 제거
    sanitize_name = os.path.basename(filename)
    # 특수문자 반환
    sanitize_name = re.sub(r'[<>:"|?*]', "_", sanitize_name)
    # 제어문자 제거
    sanitize_name = re.sub(r"[\x00-\x1f]", "", sanitize_name)
    # 윈도우 예약어 처리
    window_reserved = (
        ["CON", "PRN", "AUX", "NULL"]
        + [f"CON{i}" for i in range(1, 10)]
        + [f"LPT{i}" for i in range(1, 10)]
    )
    if sanitize_name.upper().split(".")[0] in window_reserved:
        sanitize_name = f"file_{sanitize_name}"

    if len(sanitize_name) > MAX_FILE_SIZE:
        raise HTTPException(400, f"파일명이 너무 깁니다 (최대 255자)")

    return sanitize_name


# 파일을 디스크에 저장
def save_file_to_disk(file_id: str, sanitized_name: str, contents: bytes) -> str:
    upload_dir = os.path.abspath("uploads")
    os.makedirs(upload_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = f"{file_id}_{timestamp}_{sanitized_name}"
    path = os.path.join(upload_dir, safe_name)

    final_path = os.path.abspath(path)
    if not final_path.startswith(upload_dir):
        raise HTTPException(400, "허용되지 않는 파일 경로입니다.")

    with open(path, "wb") as buf:
        buf.write(contents)

    return path


@app.post("/upload-file/")
async def upload_file(file: UploadFile = File(...)):
    # 파일 크기 검증
    file_size = validate_file_size(file)

    # 청크 단위로 파일 읽기
    contents = read_file_in_chunks(file)

    # 파일 형식 및 데이터 검증
    df = validate_file_format_and_data(file.filename, contents)

    # 파일명 정제
    sanitized_name = sanitize_filename(file.filename)

    # 파일 저장
    file_id = str(uuid.uuid4())
    path = save_file_to_disk(file_id, sanitized_name, contents)

    # 3. 메타데이터 저장
    uploaded_files[file_id] = {
        "path": path,
        "original_name": sanitized_name,
        "uploaded_at": datetime.now().isoformat(),
    }

    # 4. 다운로드 URL 포함 응답
    return {
        "file_id": file_id,
        "original_filename": file.filename,
        "safe_filename": sanitized_name,
        "download_url": f"/download/{file_id}",
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
        media_type="application/octet-stream",
    )


# 프론트에서 S3의 파일을 업로드 하기 위해 메타데이터와 함께 Presigned URL 요청
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import boto3

app = FastAPI()

# LocalStack S3 클라이언트 설정
s3_client = boto3.client(
    "s3",
    aws_access_key_id="test",
    aws_secret_access_key="test",
    region_name="us-east-1",
    endpoint_url="http://localhost:4566",
)


class FileMetadata(BaseModel):
    filename: str
    size: int
    content_type: str
    uploaded_at: str


@app.post("/presigned-url/")
async def get_presigned_url(metadata: FileMetadata):
    bucket_name = "sample-bucket"  # 실제 버킷명으로 변경
    key = f"uploads/{metadata.filename}"
    try:
        # 업로드용 presigned URL (PUT)
        presigned_put_url = s3_client.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": bucket_name,
                "Key": key,
                "ContentType": metadata.content_type,
            },
            ExpiresIn=3600,
        )
        # 다운로드용 presigned URL (GET)
        presigned_get_url = s3_client.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": bucket_name, "Key": key},
            ExpiresIn=3600,
        )
        return {
            "upload_url": presigned_put_url,
            "download_url": presigned_get_url,
            "s3_key": key,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# DynamoDB 리소스 (로컬스택 환경)
dynamodb = boto3.resource(
    "dynamodb",
    endpoint_url="http://localhost:4566",  # LocalStack용
    region_name="us-east-1",
    aws_access_key_id="test",
    aws_secret_access_key="test",
)
table = dynamodb.Table("FileMetadata")


class FileMetadata(BaseModel):
    filename: str
    s3_key: str
    size: int
    content_type: str
    uploaded_at: str


@app.post("/save-metadata/")
def save_metadata(metadata: FileMetadata):
    file_id = str(uuid.uuid4())
    item = {
        "file_id": file_id,
        "filename": metadata.filename,
        "s3_key": metadata.s3_key,
        "size": metadata.size,
        "content_type": metadata.content_type,
        "uploaded_at": metadata.uploaded_at or datetime.utcnow().isoformat(),
    }
    try:
        table.put_item(Item=item)
        return {"file_id": file_id, "message": "메타데이터 저장 성공"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
