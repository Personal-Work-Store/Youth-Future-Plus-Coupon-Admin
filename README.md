# 처음 시작

## 콘다 가상환경 설정
conda create -n Coupon_Admin python=3.11

## 콘다 가상환경 실행
conda activate Coupon_Admin

## 의존성 설치
pip install -r requirements.txt

## 현재 설치된 패키지 목록 확인 및 출력
pip freeze > requirements.txt

## Uvicorn 실행
uvicorn main:app --reload

# 기타 conda 명령어

## 콘다 비활성화
> conda deactivate

## 콘다 환경 리스트
conda env list

## 콘다 환경 삭제
> conda remove --name "환경 이름" --all

## Local Stack AWS Configure
```
(Coupon_Admin) F:\Repository\Youth-Future-Plus-Coupon-Admin>aws configure      
AWS Access Key ID [None]: test
AWS Secret Access Key [None]: test 
Default region name [None]: us-east-1
Default output format [None]: json
```

## LocalStack 명령어

### S3 버킷 생성하기
```
awslocal s3api create-bucket --bucket sample-bucket
```
결과
```
{
    "Location": "/sample-bucket"
}
```

### S3 버킷 확인하기
```
awslocal s3api list-buckets
```
결과
```
{
    "Buckets": [
        {
            "Name": "sample-bucket",
            "CreationDate": "2025-06-26T06:35:59.000Z",
            "BucketRegion": "us-east-1"
        }
    ],
    "Owner": {
        "DisplayName": "webfile",
        "ID": "75aa57f09aa0c8caeab4f8c24e99d10f8e7faeebf76c078efc7c6caea54ba06a"
    },
    "Prefix": null
}
```
### S3 버킷 파일 업로드
```
awslocal s3api put-object ^
--bucket sample-bucket ^
--key image.jpg ^
--body image.jpg
```
결과
```
{
    "ETag": "\"d1f86da6111db1c1043356588464a8f4\"",
    "ChecksumCRC32": "W80ODQ==",
    "ChecksumType": "FULL_OBJECT",
    "ServerSideEncryption": "AES256"
}
```
### 파일 목록 조회
```
awslocal s3api list-objects --bucket sample-bucket
```
결과
```
{
    "Contents": [
        {
            "Key": "image.jpg",
            "LastModified": "2025-06-26T06:39:37.000Z",
            "ETag": "\"d1f86da6111db1c1043356588464a8f4\"",
            "ChecksumAlgorithm": [
                "CRC32"
            ],
            "ChecksumType": "FULL_OBJECT",
            "Size": 32341,
            "StorageClass": "STANDARD",
            "Owner": {
                "DisplayName": "webfile",
                "ID": "75aa57f09aa0c8caeab4f8c24e99d10f8e7faeebf76c078efc7c6caea54ba06a"
            }
        }
    ],
    "RequestCharged": null,
    "Prefix": ""
}
```
### 파일 다운로드
```
awslocal s3 cp s3://sample-bucket/image.jpg ./image_downloaded.jpg
```
결과
```
download: s3://sample-bucket/image.jpg to .\image_downloaded.jpg
```