FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies cleanly
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn

# Copy project source files
COPY . /app/

# Create the database directory folder structure 
RUN mkdir -p /app/db_storage

# Collect Django static assets 
RUN python manage.py collectstatic --noinput || echo "Static mapping handled natively"

EXPOSE 8000

CMD ["gunicorn", "dds_mali.wsgi:application", "--bind", "0.0.0.0:8000"]
