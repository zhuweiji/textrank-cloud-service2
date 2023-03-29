```bash
python -m cloud_worker.main
python -m fastapi_server.main

```

```bash

docker run -p 15672:15672 -p 5672:5672 rabbitmq:3-management
docker run -p 8080:8080 shafiq98/text_rank_server:1
docker build -t --memory=64m shafiq98/text_rank_worker:1 .
```

---
https://levelup.gitconnected.com/dockerized-flask-celery-rabbitmq-redis-application-df74c837a0a1