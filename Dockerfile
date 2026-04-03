FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

# 모델 저장 디렉토리 생성
RUN mkdir -p model

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
