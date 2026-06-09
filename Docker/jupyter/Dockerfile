# Start from official Python image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file from local machine to image
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Expose Jupyter's default port
EXPOSE 8888

# Mount point for local Git repository
VOLUME ["/workspace"]

# Command to start Jupyter when container runs
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]
