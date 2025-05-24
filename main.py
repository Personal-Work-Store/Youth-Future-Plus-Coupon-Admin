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
    
    return {
        "filename": file.filename,
        "first_column_is_customer_id": first_column_check,
        "total_columns": num_columns,
        "total_rows": num_rows,
        "columns": [str(col) for col in df.columns.tolist()]  # .tolist() 추가
    }