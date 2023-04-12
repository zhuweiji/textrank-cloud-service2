next steps:
add imagerank on the frontend via sentence ranking 

Instructions
1. Modify IP Address in **cloud-worker/cloud_worker/constants.py** tp local IP
   1. NOT 127.0.0.1

In 2 different terminals, run:
```bash
> docker-compose up --build
```
```bash
> kubectl apply -f kubes_manifest
```