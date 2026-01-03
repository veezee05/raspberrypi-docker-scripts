# Use python 3.9 slim (bookworm) as base for stability
FROM python:3.9-slim-bookworm

# Install system dependencies
# - chromium: for Kiosk mode browser
# - x11-xserver-utils, xauth: for X11 forwarding
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    pcscd \
    libpcsclite-dev \
    swig \
    chromium \
    x11-xserver-utils \
    xauth \
    && rm -rf /var/lib/apt/lists/*

# Install Docker CLI
ENV DOCKER_VERSION=24.0.5
RUN curl -fsSL https://download.docker.com/linux/static/stable/x86_64/docker-${DOCKER_VERSION}.tgz -o docker.tgz \
    && tar xzvf docker.tgz --strip 1 -C /usr/local/bin docker/docker \
    && rm docker.tgz

# Set working directory
WORKDIR /app

# Install Python Dependencies
RUN pip install flask requests pyscard RPi.GPIO

# Copy source code
COPY . .

# Make entrypoint executable
RUN chmod +x entrypoint.sh

# Expose Flask Port
EXPOSE 5000

# Entrypoint
ENTRYPOINT ["./entrypoint.sh"]
