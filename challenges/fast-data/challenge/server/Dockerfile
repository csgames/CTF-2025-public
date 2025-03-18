FROM python:latest

# Install
RUN DEBIAN_FRONTEND="noninteractive" apt update
RUN DEBIAN_FRONTEND="noninteractive" apt install -y supervisor varnish

# Server
WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY . /app

# DB
RUN python /app/db.py

# Supervisord
COPY config/supervisord.conf /etc/supervisord.conf
COPY config/default.vcl /etc/varnish/default.vcl

# Run
EXPOSE 1337

ENTRYPOINT ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]
