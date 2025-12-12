FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (gcc for some python packages)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_sm

# Copy the rest of the application
COPY . .

# Create a directory for the database in a writable location if needed, 
# or ensure the current directory is writable.
# HF Spaces usually run as user 1000.
RUN chmod -R 777 /app

# Environment variables
ENV PORT=7860

# Expose the port (optional metadata)
EXPOSE 7860

# Run the application
CMD ["python", "run.py"]
