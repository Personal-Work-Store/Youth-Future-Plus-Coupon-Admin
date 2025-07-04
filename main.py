from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import boto3
import io
import csv
import uuid
from datetime import datetime

app = FastAPI()

# LocalStack S3 클라이언트 : Presigned URL 생성 등 특수 기능은 client에서만 지원
s3_client = boto3.client(
    "s3",
    aws_access_key_id="test",
    aws_secret_access_key="test",
    region_name="us-east-1",
    endpoint_url="http://localhost:4566",
)

# DynamoDB 리소스 : 테이블 아이템등 리소스 단위로 작업하는 경우가 많아 resource 방식 사용
dynamodb = boto3.resource(
    "dynamodb",
    endpoint_url="http://localhost:4566",
    region_name="us-east-1",
    aws_access_key_id="test",
    aws_secret_access_key="test",
)
# FileMetadata 테이블 객체 할당 해당 테이블이 없을경우 table 객체를 만들때는 오류가 일어나지 않지만 읽거나 쓰기 작업을 할 때 오류가 발생
table = dynamodb.Table("FileMetadata")


# Pydantic의 BaesModel을 상속받아 데이터 모델로 동작
class FileMetadata(BaseModel):
    filename: str
    size: int
    content_type: str
    uploaded_at: str


# Presigned URL 발급
@app.post("/presigned-url/")
async def get_presigned_url(metadata: FileMetadata):
    # 사용할 S3 bucket 이름
    bucket_name = "sample-bucket"
    # 업로드할 S3 오브젝트의 경로(키)를 파일명 기반으로 생성
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
        return {
            "upload_url": presigned_put_url,
            "s3_key": key,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# DynamoDB에 메타데이터 저장
@app.post("/save-metadata/")
def save_metadata(metadata: FileMetadata):
    file_id = str(uuid.uuid4())
    item = {
        # 파일 고유 식별자
        "file_id": file_id,
        # 파일 이름
        "filename": metadata.filename,
        # S3 버킷에 저장될 경로
        "s3_key": f"uploads/{metadata.filename}",
        # 파일 크기
        "size": metadata.size,
        # 파일의 MIME 타입
        "content_type": metadata.content_type,
        # 업로드 시각
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
        # Bucket의 Key 파일의 바이너리 스트림과 메타데이터를 response에 저장
        response = s3_client.get_object(Bucket=info.bucket, Key=info.key)
        # 바이너리스트림을 텍스트 스트림으로 변환
        stream = io.TextIOWrapper(response["Body"], encoding="utf-8")
        # CSV 파일을 한 줄씩 읽을 준비
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
