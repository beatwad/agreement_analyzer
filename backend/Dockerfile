FROM python:3.13.9-trixie

WORKDIR /app/backend
ENV UV_PROJECT_ENVIRONMENT=/app/.venv

COPY pyproject.toml uv.lock /app/backend/
RUN pip install --no-cache-dir uv && \
    uv sync --frozen --no-dev && \
    uv run playwright install --with-deps chromium

COPY backend/ /app/backend/

EXPOSE 8001

CMD ["uv", "run", "uvicorn", "server:app", "--reload", "--host", "0.0.0.0", "--port", "8001"]