FROM ubuntu


RUN apt-get update
RUN apt-get install -y nginx uwsgi python-pip uwsgi-plugin-python jq
RUN pip install virtualenv

RUN mkdir -p /etc/app
WORKDIR /etc/app

RUN virtualenv .venv
ADD ./venv.pth /etc/app/.venv/lib/python2.7/site-packages/venv.pth
ADD ./server /etc/app/server
RUN .venv/bin/pip install -r /etc/app/server/requirements.txt

ENTRYPOINT ["/etc/app/.venv/bin/python", "/etc/app/server/app.py", "flask", "run"]
