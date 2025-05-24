from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "쿠폰 시스템 ADMIN API에 오신 것을 환영합니다."}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

from fastapi import UploadFile, File

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    return {"filename" : file.filename}

import pandas as pd
from io import StringIO, BytesIO

@app.post("/upload-file/")
async def upload_check_file(file: UploadFile = File(...)):
    contents = await file.read()
    file_extension = file.filename.split(".")[-1].lower()
    
    if file_extension == "csv":
        # CSV 파일 처리
        s = StringIO(contents.decode('utf-8'))
        df = pd.read_csv(s)
    elif file_extension in ["xlsx", "xls"]:
        # Excel 파일 처리
        excel_data = BytesIO(contents)
        df = pd.read_excel(excel_data)
    else:
        return {"error": "지원되지 않는 파일 형식입니다. CSV 또는 Excel 파일만 업로드해주세요."}
    
    # 데이터프레임 검증
    if df.empty:
        return {"error": "파일에 데이터가 없습니다."}
    
    if len(df.columns) == 0:
        return {"error": "파일에 컬럼이 없습니다."}
    
    # 헤더 확인
    first_column_check = df.columns[0] == 'customer_id'
    

    # 최소 컬럼 개수 확인
    if len(df.columns) != 1:
        return {
            "error": "컬럼은 하나만 필요합니다.",
            "len(df.columns)" : len(df.columns)
            }
    
    # customer_id 컬럼 확인
    if not first_column_check:
        return {
            "error": "첫 번째 컬럼이 'customer_id'가 아닙니다.",
            "actual_first_column": df.columns[0]
        }
    
    return {
        "filename": file.filename,
        "first_column_is_customer_id": first_column_check,
        "total_columns": len(df.columns),
        "total_rows": len(df),
        "columns": list(df.columns)
    }
