# syntax=docker/dockerfile:1
ARG BASE_IMAGE=ubuntu:22.04

FROM ${BASE_IMAGE}
ENV DEBIAN_FRONTEND=noninteractive

# PrairieLearn workspace image: one container per student, proxied by PrairieLearn.
# gcc/libc6-dev: compile the vulnerable program at runtime (from /sync-challenge).
# gdb-minimal: no Python scripting needed; python3 is for the server and egg.py.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 python3-venv gdb-minimal gcc libc6-dev util-linux && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1001 -s /usr/sbin/nologin student && chmod 755 /home/student

WORKDIR /app
RUN python3 -m venv /opt/venv
COPY requirements.txt .
RUN /opt/venv/bin/pip install --no-cache-dir -r requirements.txt
COPY server.py launcher.py ./
COPY gdb/ /opt/gdb/

RUN chown -R root:root /app /opt/gdb /opt/venv && \
    chmod -R a+rX,go-w /app /opt/gdb /opt/venv && \
    find / -xdev -perm /6000 -type f -exec chmod a-s {} + 2>/dev/null || true

# Home for the student; PrairieLearn copies the question's workspace/ files here.
ENV GDB_HOME=/home/student

# 1 = gdb starts the program through /bin/sh so `run $(python3 egg.py)` works.
# 0 = strict (no shell), but egg.py cannot be used from `run`.
ENV GDB_RUN_USES_SHELL=1

# Read by PrairieLearn so info.json does not have to repeat them.
#  port:        where server.py listens
#  home:        base for starter files and graded files
#  rewrite-url: "true" = the container sees requests as coming from /
LABEL com.prairielearn.workspace.port="5000" \
      com.prairielearn.workspace.home="/home/student" \
      com.prairielearn.workspace.rewrite-url="true"

EXPOSE 5000
# PrairieLearn runs workspaces as 1001:1001 in production; do the same here so
# local testing matches (the `student` user above is uid 1001).
USER 1001:1001
ENTRYPOINT ["/opt/venv/bin/python", "-u", "/app/server.py"]
