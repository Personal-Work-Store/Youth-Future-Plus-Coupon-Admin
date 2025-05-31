import requests
import io

# 정상 CSV 데이터
csv_content = """customer_id
10001
10002
10003"""

# 악의적인 파일명으로 업로드 테스트
malicious_filenames = [
    "../../../etc/passwd.csv",
    "../../secret.csv", 
    "a" * 1000 + ".csv", # 긴 파일명
    "file<>:|?*.csv", # 특수문자
    "/etc/passwd.csv",
    "..\\..\\config.csv",
    "normal.csv\x00.exe",  # NULL 바이트
    "con.csv",  # 윈도우 예약어
    "prn.csv"   # 윈도우 예약어
]

for filename in malicious_filenames:
    print(f"\n=== 테스트: {filename} ===")
    
    files = {
        'file': (filename, csv_content, 'text/csv')
    }
    
    response = requests.post('http://localhost:8000/upload-file/', files=files)
    print(f"상태코드: {response.status_code}")
    print(f"응답: {response.json()}")
