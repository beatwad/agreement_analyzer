FROM python:3.13.9-trixie

WORKDIR /app

# Install system dependencies required for Playwright
# We install these first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    playwright install --with-deps chromium

# Install Tailscale
RUN curl -fsSL https://tailscale.com/install.sh | sh

COPY . .
COPY start.sh .
RUN chmod +x start.sh

# Set environment variables
EXPOSE 8001

CMD ["/bin/bash", "./start.sh"]

