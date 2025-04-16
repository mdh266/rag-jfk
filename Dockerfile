FROM python:3.11-slim

RUN mkdir -p /work/app
WORKDIR /work

COPY app/ /work/app
COPY pyproject.toml /work
COPY entrypoint.sh /work
RUN chmod +x /work/entrypoint.sh 
RUN pip install . --no-cache 

ENTRYPOINT ["/work/entrypoint.sh"]
