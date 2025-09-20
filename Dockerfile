# Use Python 3.9 slim image as base
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Create a non-root user for security
RUN useradd -m -u 1000 user

# Copy the rest of the application
COPY --chown=user . /home/user/app

# Switch to user
USER user

# Set environment variables
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Change to user's home directory
WORKDIR /home/user/app

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Make startup script executable
RUN chmod +x start.sh

# Run Streamlit via startup script
CMD ["./start.sh"]