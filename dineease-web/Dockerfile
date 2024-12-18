# Use the latest Python image
FROM python:3.11

# Install system dependencies, including GDAL and PostgreSQL
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    postgresql \
    postgresql-contrib \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set GDAL environment variables
ENV GDAL_LIBRARY_PATH=/usr/lib/libgdal.so
ENV PATH="$PATH:/usr/lib"

# Set the working directory
WORKDIR /app

# Install Python dependencies before copying the full source code for better caching
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Django project files
COPY . .

# Collect static files (uncomment for production builds)
# RUN python manage.py collectstatic --noinput

# Expose the Django port
EXPOSE 8000

# Start the Django server using Daphne for ASGI applications
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "dineease_backend.asgi:application"]
