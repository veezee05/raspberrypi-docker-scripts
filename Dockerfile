# Use python 3.9 slim as base
FROM python:3.9-slim

# Install system dependencies
# - docker: to allow the blockchain_client.py to run `docker exec` commands (Docker-in-Docker client side)
# - pcscd, libpcsclite-dev, swig: for pyscard (Smart Card)
# - build-essential: for compiling python modules
# - curl: to install docker
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    pcscd \
    libpcsclite-dev \
    swig \
    && rm -rf /var/lib/apt/lists/*

# Install Docker CLI
# Install Docker CLI (Static Binary to avoid repo issues on Debian Trixie/Testing)
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

# Expose Flask Port
EXPOSE 5000

# Entrypoint
CMD ["python", "server.py"]
