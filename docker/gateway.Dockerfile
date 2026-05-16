FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml .
RUN pip install -e .

COPY shared/ shared/
COPY agents/base/ agents/base/
COPY agents/__init__.py agents/__init__.py
COPY gateway/ gateway/

ENV PYTHONUNBUFFERED=1
CMD ["uvicorn", "gateway.main:app", "--host", "0.0.0.0", "--port", "8000"]
