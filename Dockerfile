

# Use official Python 3.11 image
FROM python:3.11

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Alembic configuration and migrations
COPY alembic.ini .
COPY alembic ./alembic

# Copy application code
COPY app ./app

# Expose port
EXPOSE 8000

# Run database migrations and start the server
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]