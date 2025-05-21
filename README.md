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