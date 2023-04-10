FROM python:3.10-slim-buster
RUN apt-get update \
    && apt-get install g++ -y \
    && apt-get clean

WORKDIR /app
COPY requirements.txt /app/
RUN pip install -r requirements.txt
RUN python -m spacy download en_core_web_lg

COPY . .
ENTRYPOINT python3 -m cloud_worker.main
