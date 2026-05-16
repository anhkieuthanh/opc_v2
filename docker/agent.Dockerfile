FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml .
RUN pip install -e .

COPY shared/ shared/
COPY agents/ agents/

ENV PYTHONUNBUFFERED=1
