FROM python:3.10-slim

WORKDIR /app

# 루트 requirements.txt를 backend에서 사용한다고 가정
COPY ../requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

# backend 폴더 전체 복사
COPY . .

# FastAPI 서버 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
