# Use python 3.9 slim (bookworm) as base for stability
FROM python:3.9-slim-bookworm

# Install system dependencies, Docker CLI, and Python packages via consolidated script
COPY setup_scripts/ ./setup_scripts/
RUN chmod +x setup_scripts/*.sh && \
    ./setup_scripts/install_all.sh

# Set working directory
WORKDIR /app

# Copy source code
COPY . .

# Make entrypoint executable
RUN chmod +x entrypoint.sh

# Expose Flask Port
EXPOSE 5000

# Entrypoint
ENTRYPOINT ["./entrypoint.sh"]
