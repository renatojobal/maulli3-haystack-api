### After first installation

Open two terminals and run the following commands in each of them:

Make sure docker daemon is running, for that you could open docker desktop.

```bash
docker run -p 127.0.0.1:9200:9200 -p 127.0.0.1:9300:9300 -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch:7.17.15
```

```bash
source venv/bin/activate

gunicorn rest_api.application:app -b 0.0.0.0:8000 -k uvicorn.workers.UvicornWorker -t 300
```
