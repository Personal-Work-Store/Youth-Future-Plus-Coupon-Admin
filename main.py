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
import os
from datetime import datetime
import shutil

@app.post("/upload-file/")
async def upload_check_file(file: UploadFile = File(...)):
    contents = await file.read()
    file_extension = file.filename.split(".")[-1].lower()
    
    try:
        if file_extension == "csv":
            s = StringIO(contents.decode('utf-8'))
            df = pd.read_csv(s)
        elif file_extension in ["xlsx", "xls"]:
            excel_data = BytesIO(contents)
            df = pd.read_excel(excel_data)
        else:
            return {"error": "지원되지 않는 파일 형식입니다. CSV 또는 Excel 파일만 업로드해주세요."}
    except pd.errors.EmptyDataError:
        return {"error" : "파일에 읽을 수 있는 데이터가 없습니다."}
    
    # 1. 완전히 빈 파일 체크
    if df.empty:
        return {"error": "파일에 데이터가 없습니다."}
    
    # numpy 타입을 확실히 Python 타입으로 변환
    num_columns = int(len(df.columns)) if hasattr(len(df.columns), 'item') else len(df.columns)
    num_rows = int(len(df)) if hasattr(len(df), 'item') else len(df)

    # 2. 컬럼 개수 체크 (먼저 체크)
    if num_columns != 1:
        return {
            "error": "컬럼은 하나만 필요합니다.",
            "len(df.columns)": num_columns
        }
    
     # 컬럼명도 확실히 Python str로 변환
    first_column = str(df.columns[0])
    first_column_check = first_column == 'customer_id'
    
    if not first_column_check:
        return {
            "error": "첫 번째 컬럼이 'customer_id'가 아닙니다.",
            "actual_first_column": first_column
        }
    
    if num_rows == 0:
        return {"error": "회원 목록이 비어있습니다."}
    
    # 파일 저장 전에 파일 포인터를 처음으로 되돌리기
    await file.seek(0)

    # 파일 저장
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    # 안전한 파일명 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(upload_dir, safe_filename)
    
    # 파일 저장
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "filename": file.filename,
        "first_column_is_customer_id": first_column_check,
        "total_columns": num_columns,
        "total_rows": num_rows,
        "columns": [str(col) for col in df.columns.tolist()]  # .tolist() 추가
    }