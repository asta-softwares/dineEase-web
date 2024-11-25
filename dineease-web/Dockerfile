# Use the latest Python image
FROM python:3.11

# Install system dependencies, including GDAL
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    postgresql \
    postgresql-contrib \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set GDAL_LIBRARY_PATH environment variable
ENV GDAL_LIBRARY_PATH=/usr/lib/libgdal.so
ENV PATH="$PATH:/usr/lib"

# Set working directory
WORKDIR /app

# Copy requirements.txt and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Django project files
COPY . .

# Collect static files
# RUN python manage.py collectstatic --noinput

# Expose the Django port
EXPOSE 8000

# Start the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
