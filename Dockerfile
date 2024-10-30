# Python 3.9 베이스 이미지 사용
FROM python:3.12

# 작업 디렉토리 설정
WORKDIR /NHS-Backend-API

# 필요한 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# FastAPI 앱 복사
COPY . .

# 컨테이너의 기본 포트 설정
EXPOSE 1500

# Uvicorn으로 FastAPI 앱 실행
CMD ["python3", "main.py"]
#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "1500", "--workers", "10"]
