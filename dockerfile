FROM python:3.12-slim

# Install build dependencies and GPIO libraries
RUN apt-get update && apt-get install -y \
    build-essential \
    libgpiod2 \
    git \
    python3-dev \
    python3-pip \
    gcc \
    libc-dev \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Copy application code
COPY app.py .
COPY sds011.py .
COPY indoorweather.py .
COPY outdoorweather.py .
COPY influx.py .
COPY config.ini .

# Run application
CMD ["python", "app.py"]