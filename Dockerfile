# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy poetry files first (for better caching)
COPY pyproject.toml poetry.lock* ./

# Configure poetry to not create virtual environment
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --only=main --no-root

# Copy application files
COPY . .

# Create storage directory with proper permissions
RUN mkdir -p /app/storage && chmod 755 /app/storage

# Expose port 3000
EXPOSE 3000

# Run the application
CMD ["python", "main.py"]
