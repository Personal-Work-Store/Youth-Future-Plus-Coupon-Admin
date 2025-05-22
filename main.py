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
    
    # 헤더 확인
    first_column_check = df.columns[0] == 'customer_id'
        
    
    return {
        "filename": file.filename,
        "first_column_is_customer_id": first_column_check
    }
