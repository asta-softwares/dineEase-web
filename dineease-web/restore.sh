#!/bin/bash

# Define input arguments
POSTGRES_CONTAINER=$1
DUMP_FILE=$2
ZIP_FILE=$3

# Logging
echo "Restoring database and uploads..."

# Validate input arguments
if [ -z "$POSTGRES_CONTAINER" ]; then
    echo "Error: PostgreSQL container name not provided."
    echo "Usage: ./restore.sh <postgres_container> <db_dump_file> <uploads_zip_file>"
    exit 1
fi

if [ -z "$DUMP_FILE" ]; then
    echo "No database dump file provided. Skipping database restoration."
else
    echo "Restoring database from dump: $DUMP_FILE"

    # Terminate active connections
    echo "Terminating active connections to the database..."
    docker exec $POSTGRES_CONTAINER psql -U postgres -c "SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = 'postgres' AND pid <> pg_backend_pid();"

    # Drop and recreate the database
    echo "Dropping the existing database..."
    docker exec $POSTGRES_CONTAINER dropdb -U postgres postgres

    echo "Creating a new database..."
    docker exec $POSTGRES_CONTAINER createdb -U postgres postgres

    # Restore the database with schema and data
    echo "Restoring the database from the dump file..."
    docker exec -i $POSTGRES_CONTAINER psql -U postgres postgres < "$DUMP_FILE"
    if [ $? -eq 0 ]; then
        echo "Database restoration completed successfully."
    else
        echo "Database restoration failed."
        exit 1
    fi
fi

if [ -z "$ZIP_FILE" ]; then
    echo "No uploads zip file provided. Skipping uploads restoration."
else
    echo "Restoring uploads from zip: $ZIP_FILE"
    # Check for unzip utility
    if ! command -v unzip &> /dev/null; then
        echo "Unzip utility not found. Installing..."
        sudo apt install -y unzip
    fi

    # Unzip and copy files to the media directory
    unzip -o "$ZIP_FILE" -d ./media_temp
    cp -a ./media_temp/* ./media/
    rm -rf ./media_temp
    if [ $? -eq 0 ]; then
        echo "Uploads restoration completed successfully."
    else
        echo "Uploads restoration failed."
        exit 1
    fi
fi

echo "Restoration process completed."
exit 0
