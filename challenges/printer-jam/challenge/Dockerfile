#
# Copyright(C) 1993-1996 ZEROZ, Inc.
#
# This program is non-free software; you cannot redistribute it and/or
# modify it under the terms of the ZEROZ License
# as published by the ZEROZ Foundation.
#
# DESCRIPTION:
#   Setup printer.
#

FROM ubuntu:24.04

# Install requirements
RUN apt update
RUN DEBIAN_FRONTEND=noninteractive apt -y install gcc socat sudo
RUN rm -rf /var/lib/apt/lists/*

# Build args
ARG FLAG1="FLAG1"
ARG FLAG2="FLAG2"
ARG FLAG3="FLAG3"
ARG FLAG4="FLAG4"

# Create worker
WORKDIR /home/worker

COPY worker .

RUN sed -i -e "s/\"FLAG1\"/\"${FLAG1}\"/g" main.c
RUN gcc -w -Wl,-z,relro,-z,now -no-pie main.c -o worker && rm main.c main.h

COPY files/log log
RUN sed -i -e "s/FLAG2/${FLAG2}/g" log

RUN sed -i -e "s/\"FLAG3\"/\"${FLAG3}\"/g" help.c
RUN gcc help.c -o help && rm help.c

# Create printer
WORKDIR /printer

COPY printer .

RUN touch /printer/page

RUN sed -i -e "s/\"FLAG4\"/\"${FLAG4}\"/g" debug.c
RUN gcc debug.c -o debug && rm debug.c

# Create users
RUN groupadd worker && useradd -g worker worker

# System config
COPY --chown=root:root files/sudoers /etc/sudoers.d/sudoers

# Permissions
RUN chown -R root:worker /home/worker
RUN chmod -R 775 /home/worker

RUN chmod 740 /home/worker/log
RUN chmod 710 /home/worker/help /home/worker/worker

RUN chown -R root:root /printer
RUN chmod -R 775 /printer

RUN chmod 777 /printer/page
RUN chmod 710 /printer/debug
RUN chmod 754 /printer/print.sh /printer/queue.sh /printer/unjam.sh

# Create service directory
WORKDIR /home/worker

EXPOSE 9001
CMD su -c "socat TCP-LISTEN:9001,fork,reuseaddr EXEC:/home/worker/worker,pty,echo=0,raw" - worker
