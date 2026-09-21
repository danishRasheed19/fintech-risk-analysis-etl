FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY data ./data
COPY reports ./reports

ENV PYTHONPATH=/app/src


CMD ["python", "-m", "src.pipeline"]