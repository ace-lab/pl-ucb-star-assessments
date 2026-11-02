# syntax=docker/dockerfile:1
ARG BASE_IMAGE=ubuntu:22.04

############ stage 1: compile the programs students will debug ############
FROM ${BASE_IMAGE} AS build
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libc6-dev make && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /opt/challenge
COPY challenge/ .
# Replace demo.c with your vulnerable program and adjust flags as needed
# (e.g. -fno-stack-protector -no-pie -z execstack for classic exploit labs).
RUN gcc -g -O0 -o demo demo.c

############ stage 2: runtime image (no compiler) ############
FROM ${BASE_IMAGE}
ENV DEBIAN_FRONTEND=noninteractive
# gdb-minimal has no Python scripting; python3 is for the server and egg.py.
RUN apt-get update && \
    apt-get install -y --no-install-recommends python3 python3-venv gdb-minimal util-linux && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1001 -s /usr/sbin/nologin student && chmod 755 /home/student
WORKDIR /app
RUN python3 -m venv /opt/venv
COPY requirements.txt .
RUN /opt/venv/bin/pip install --no-cache-dir -r requirements.txt
COPY server.py launcher.py ./
COPY gdb/ /opt/gdb/
COPY --from=build /opt/challenge /opt/challenge
RUN chown -R root:root /app /opt/gdb /opt/challenge /opt/venv && \
    chmod -R a+rX,go-w /app /opt/gdb /opt/challenge /opt/venv && \
    find / -xdev -perm /6000 -type f -exec chmod a-s {} + 2>/dev/null || true

# The Flask server runs as root and starts gdb as UID 1001 (via setpriv).
ENV PROGRAM_ARGS='["/opt/challenge/demo"]'
# 1 = gdb starts the program through /bin/sh so `run $(python3 egg.py)` works.
# 0 = strict (no shell), but egg.py cannot be used from `run`.
ENV GDB_RUN_USES_SHELL=1

EXPOSE 5000
ENTRYPOINT ["/opt/venv/bin/python", "-u", "/app/server.py"]
