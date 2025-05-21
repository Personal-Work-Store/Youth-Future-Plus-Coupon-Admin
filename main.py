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