import mimetypes
import os
from datetime import datetime
import requests

# 파일 메타데이터 추출 함수
def extract_metadata(file_path):
    file_stat = os.stat(file_path)
    content_type, _ = mimetypes.guess_type(file_path)
    metadata = {
        "filename": os.path.basename(file_path),
        "size": file_stat.st_size,
        "content_type": content_type or "application/octet-stream",
        "uploaded_at": datetime.now().isoformat()
    }
    return metadata

# 실제 사용할 파일 경로로 변경하세요
file_path = "TestFile/test1_normal.csv"
metadata = extract_metadata(file_path)

# presigned URL 요청 API 엔드포인트 (실제 주소로 변경 필요)
api_url = "http://localhost:8000/presigned-url/"

# presigned URL 요청 함수
def request_presigned_url(metadata):
    response = requests.post(api_url, json=metadata)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get presigned URL: {response.status_code} {response.text}")
        return None

# presigned URL 요청 및 결과 출력
presigned_url_response = request_presigned_url(metadata)

print("Extracted Metadata:", metadata)
print("Presigned URL Response:", presigned_url_response)