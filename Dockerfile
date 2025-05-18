FROM python:latest

ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get install -y iproute2
RUN mkdir /web
WORKDIR /
COPY web/ /web/
COPY requirements.txt /
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r  requirements.txt && rm requirements.txt
# Clean up
RUN apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /web
RUN chmod +x docker-entrypoint.sh
ENTRYPOINT ./docker-entrypoint.sh