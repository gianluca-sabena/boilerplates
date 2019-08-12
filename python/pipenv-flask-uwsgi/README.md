# Understand python ecosystem

Tools:

- pyenv install python interpreter
- pipenv create a virtual environment based on Pipfile

## Run

### Flask

- `cd hello-world-pipenv`
- `export FLASK_APP=src/web.py`
- `pipenv run flask run`

## Docker

Build `docker build -t hello-world-pipenv -f Dockerfile.centos .`

Run `docker run -t -i  hello-world-pipenv pipenv run python -u src/main.py`

Run with random user `docker run -t -i --user 10111:0 hello-world-pipenv`

Run flask (1) `docker run -t -i -p 9090:9090 --user 10111:0 hello-world-pipenv uwsgi /opt/app/config/flask.ini`

Run flask (1) `docker run -t -i -p 9090:9090 --user 10111:0 hello-world-pipenv uwsgi --virtualenv /opt/app/.venv/ --chdir /opt/app/web  -s /tmp/yourapplication.sock --manage-script-name --mount /=wsgi:app --http-socket=0.0.0.0:9090`

(1) - Follow uwsgi doc <https://flask.palletsprojects.com/en/1.1.x/deploying/uwsgi/>
