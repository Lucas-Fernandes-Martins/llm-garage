# Use an official lightweight Python runtime as the base image
FROM python:3.13-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential \
      git && \
    rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONUNBUFFERED=1
# Set the WS_UPDATE_URL to point to your backend's websocket producer endpoint
ENV WS_UPDATE_URL="ws://your-backend.example.com/ws/producer"

# Set the working directory
WORKDIR /app

# Copy your requirements file and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of your code into the container
COPY . /app

# Specify the command to run your training job
# These arguments can be overridden when you submit the custom job
CMD ["python", "main.py", "--dataset_path", "your_dataset.json", "--epochs", "3", "--learning_rate", "0.0002", "--lora_rank", "4"]
