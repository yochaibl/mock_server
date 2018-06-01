FROM ubuntu


RUN apt-get update
RUN apt-get install -y nginx uwsgi python-pip uwsgi-plugin-python
RUN pip install virtualenv

RUN mkdir -p /etc/app
WORKDIR /etc/app

RUN virtualenv .venv
ADD ./server /etc/app/src
RUN .venv/bin/pip install -r /etc/app/src/requirements.txt

ENTRYPOINT ["/etc/app/.venv/bin/python", "/etc/app/src/server.py", "flask", "run"]
