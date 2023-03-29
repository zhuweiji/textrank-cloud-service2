FROM python:3.10-slim-buster
RUN apt-get update \
    && apt-get install g++ -y \
    && apt-get clean

WORKDIR /app
COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY . .
ENTRYPOINT  uvicorn fastapi_server.main:app --host 0.0.0.0 --port 8080


