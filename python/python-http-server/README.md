# Deploy flask with uwsgi and nginx

## Help

- Flask with uwsgi <https://uwsgi-docs.readthedocs.io/en/latest/WSGIquickstart.html#deploying-flask>

## Build and run

Build docker `docker build -t flask .`

Run `docker run -t -i -p 8080:8080 -p 9090:9090 -p 9191:9191 flask`

Ports:

- 8080 nginx reverse proxy
- 9090 uwsgi http socket
- 9191 uwsgi stats (debug use only)
