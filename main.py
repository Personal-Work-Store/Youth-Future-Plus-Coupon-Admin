from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import boto3
import io
import csv
import uuid
from datetime import datetime

app = FastAPI()

# LocalStack S3 클라이언트 설정
s3_client = boto3.client(
    "s3",
    aws_access_key_id="test",
    aws_secret_access_key="test",
    region_name="us-east-1",
    endpoint_url="http://localhost:4566",
)

# DynamoDB 리소스 (로컬스택 환경)
dynamodb = boto3.resource(
    "dynamodb",
    endpoint_url="http://localhost:4566",
    region_name="us-east-1",
    aws_access_key_id="test",
    aws_secret_access_key="test",
)
table = dynamodb.Table("FileMetadata")


# 메타데이터 모델
class FileMetadata(BaseModel):
    filename: str
    size: int
    content_type: str
    uploaded_at: str


# Presigned URL 발급
@app.post("/presigned-url/")
async def get_presigned_url(metadata: FileMetadata):
    bucket_name = "sample-bucket"
    key = f"uploads/{metadata.filename}"
    try:
        presigned_put_url = s3_client.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": bucket_name,
                "Key": key,
                "ContentType": metadata.content_type,
            },
            ExpiresIn=3600,
        )
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


# DynamoDB에 메타데이터 저장
@app.post("/save-metadata/")
def save_metadata(metadata: FileMetadata):
    file_id = str(uuid.uuid4())
    item = {
        "file_id": file_id,
        "filename": metadata.filename,
        "s3_key": f"uploads/{metadata.filename}",
        "size": metadata.size,
        "content_type": metadata.content_type,
        "uploaded_at": metadata.uploaded_at or datetime.utcnow().isoformat(),
    }
    try:
        table.put_item(Item=item)
        return {"file_id": file_id, "message": "메타데이터 저장 성공"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# S3 스트리밍 검증 엔드포인트
class S3FileInfo(BaseModel):
    bucket: str
    key: str


@app.post("/validate-s3-csv/")
def validate_s3_csv(info: S3FileInfo):
    """
    S3에 저장된 대용량 CSV 파일을 스트리밍으로 읽으면서
    1. 헤더가 customer_id 하나인지
    2. 데이터가 비어있지 않은지
    를 검증합니다.
    """
    try:
        response = s3_client.get_object(Bucket=info.bucket, Key=info.key)
        stream = io.TextIOWrapper(response["Body"], encoding="utf-8")
        reader = csv.reader(stream)
        # 헤더 검증
        try:
            header = next(reader)
        except StopIteration:
            raise HTTPException(400, "파일이 비어 있습니다.")
        if len(header) != 1 or header[0] != "customer_id":
            raise HTTPException(400, "헤더가 customer_id 하나만 있어야 합니다.")
        # 데이터 유무 검증
        try:
            first_row = next(reader)
        except StopIteration:
            raise HTTPException(400, "회원 목록이 비어 있습니다.")
        # 검증 통과
        return {
            "bucket": info.bucket,
            "key": info.key,
            "header": header,
            "message": "파일 검증 통과",
        }
    except Exception as e:
        raise HTTPException(500, f"S3 파일 검증 중 오류 발생: {str(e)}")
