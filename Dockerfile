# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy poetry files
COPY pyproject.toml ./

# Configure poetry to not create virtual environment
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-dev

# Copy application files
COPY . .

# Create storage directory
RUN mkdir -p /app/storage

# Expose port 3000
EXPOSE 3000

# Run the application
CMD ["python", "main.py"]
