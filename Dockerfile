# Use Python runtime
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies and package
RUN pip install --upgrade pip && \
    pip install .

# Default command runs CLI
CMD ["rfm"]
