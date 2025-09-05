#!/bin/bash

# Set default values if not provided
CELERY_WORKERS=${CELERY_WORKERS:-4}
CELERY_QUEUE=${CELERY_QUEUE:-default}

# Check environment variables and run the appropriate command
if [ "$CELERY_BEAT" = "true" ]; then
    echo "Starting Celery Beat..."
    exec python /app/src/start_celery.py --beat
elif [ "$CELERY_FLOWER" = "true" ]; then
    echo "Starting Celery Flower..."
    exec celery --broker=$CELERY_BROKER_URL flower
elif [ "$CELERY_WORKER" = "true" ]; then
    echo "Starting Celery Worker..."
    exec python /app/src/start_celery.py --workers=$CELERY_WORKERS --queue=$CELERY_QUEUE
else
    # Run the default command if no specific role is set
    echo "Starting FastAPI application..."
    exec python /app/src/main.py
fi
