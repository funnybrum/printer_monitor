# Use a lightweight Python base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install OpenCV dependencies (needed for cv2.VideoCapture)
# The 'appuser' needs sudo to run these commands
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsm6 \
    libxext6 && \
    rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN useradd -m appuser
USER appuser

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY src/ ./src
COPY config/ ./config

# Set the entrypoint
ENTRYPOINT ["python", "-m", "src.monitor"]
