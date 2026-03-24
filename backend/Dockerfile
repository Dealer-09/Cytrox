FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY app app/
COPY main.py .

# Expose port
EXPOSE 5000

# Run app
CMD ["python", "-m", "gunicorn", "--worker-class", "eventlet", "-w", "1", "--bind", "0.0.0.0:5000", "main:app"]
