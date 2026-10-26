FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends gdb gcc libc6-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir flask flask-sock flask-cors

RUN useradd -m -s /bin/bash student
WORKDIR /app
COPY server.py .
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

USER student
EXPOSE 5000

ENTRYPOINT ["/app/entrypoint.sh"]