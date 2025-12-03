FROM python:3.13.9-trixie
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install system dependencies required for Playwright
# We install these first to leverage Docker cache
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-install-project --no-dev

# Add virtual environment to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Install Playwright browsers
RUN playwright install --with-deps chromium

COPY . .

# Set environment variables
EXPOSE 8001

CMD ["uv", "run", "uvicorn", "server:app", "--reload", "--host", "0.0.0.0", "--port", "8001"]
