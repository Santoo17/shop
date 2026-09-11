
FROM python:3.11-slim AS builder

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN pip install uv
RUN uv sync --frozen 

COPY . .

FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /app /app

ENV PATH="/app/.venv/bin:$PATH"


EXPOSE 8000

ENTRYPOINT ["sh", "-c", "python -m app.core.seed && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"]