#!/bin/bash

# MANUAL BACKUP: pg_dump -U postgres -h localhost -p 5432 postgres > db_backup.sql

# Set the backup filenames
DATE=$(date +'%Y-%m-%d_%H-%M-%S')
DB_DUMP="db_backup_$DATE.sql"
UPLOADS_ZIP="uploads_backup_$DATE.zip"

# Get the PostgreSQL container name as an argument or prompt for it
if [ -z "$1" ]; then
    echo "Enter the PostgreSQL container name: "
    read POSTGRES_CONTAINER
else
    POSTGRES_CONTAINER=$1
fi

# Check if the container name is provided
if [ -z "$POSTGRES_CONTAINER" ]; then
    echo "Error: PostgreSQL container name not provided!"
    docker ps --format '{{.Names}}'
    exit 1
fi

echo "Found PostgreSQL container: $POSTGRES_CONTAINER"

# Database backup
echo "Starting database backup..."
docker exec $POSTGRES_CONTAINER pg_dump -U postgres postgres > "$DB_DUMP"
if [ $? -eq 0 ]; then
    echo "Database backup saved as $DB_DUMP."
else
    echo "Database backup failed."
    exit 1
fi

# Uploads backup
echo "Starting uploads directory backup..."
if [ -d ./uploads ]; then
    zip -r "$UPLOADS_ZIP" ./uploads
    if [ $? -eq 0 ]; then
        echo "Uploads backup saved as $UPLOADS_ZIP."
    else
        echo "Uploads backup failed."
        exit 1
    fi
else
    echo "Uploads directory not found. Skipping uploads backup."
fi

echo "Backup completed successfully."
exit 0
