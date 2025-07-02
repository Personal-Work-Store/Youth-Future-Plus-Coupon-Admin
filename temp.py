import boto3

s3_client = boto3.client(
    "s3",
    endpoint_url="http://localhost:4566",
    aws_access_key_id="test",
    aws_secret_access_key="test",
    region_name="us-east-1",
)

response = s3_client.list_buckets()
buckets = response.get("Buckets", [])
if buckets:
    print("Buckets:")
    for bucket in buckets:
        print(f"  - {bucket['Name']}")
else:
    print("No buckets found.")

import boto3

# LocalStack 환경이라면 endpoint_url을 반드시 지정해야 합니다.
s3 = boto3.client(
    "s3",
    aws_access_key_id="test",  # LocalStack 기본값
    aws_secret_access_key="test",  # LocalStack 기본값
    region_name="us-east-1",  # LocalStack 기본값
    endpoint_url="http://localhost:4566",  # LocalStack S3 엔드포인트
)

# 다운로드용 presigned URL 생성 (GET)
url = s3.generate_presigned_url(
    ClientMethod="get_object",
    Params={"Bucket": "sample-bucket", "Key": "image.jpg"},
    ExpiresIn=3600,  # URL 유효 시간(초)
)
print("Presigned GET URL:", url)

# 업로드용 presigned URL 생성 (PUT)
put_url = s3.generate_presigned_url(
    ClientMethod="put_object",
    Params={"Bucket": "sample-bucket", "Key": "new_image.jpg"},
    ExpiresIn=3600,
)
print("Presigned PUT URL:", put_url)
