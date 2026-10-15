# 경량 파이썬 이미지 사용
FROM python:3.11-slim

# 버퍼링 비활성화 (로그 즉시 출력)
ENV PYTHONUNBUFFERED True

WORKDIR /app

# 종속성 파일 복사 및 설치
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 소스 복사
COPY . ./

# Cloud Run 표준 포트($PORT)로 Gunicorn WSGI 바인딩
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
