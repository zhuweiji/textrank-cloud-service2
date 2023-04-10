FROM python:3.10-slim-buster
RUN apt-get update \
    && apt-get clean

WORKDIR /app
COPY requirements.txt /app/
RUN pip install -r requirements.txt
RUN python3 -m spacy download en_core_web_lg

COPY . .
ENTRYPOINT python3 -m cloud_worker.main
