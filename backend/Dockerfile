FROM python:3.13.9-trixie

WORKDIR /app

# Install system dependencies required for Playwright
# We install these first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    playwright install --with-deps chromium

COPY . .

# Set environment variables
EXPOSE 8001

CMD uvicorn server:app --host 0.0.0.0 --port 8001

