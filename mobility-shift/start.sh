#!/bin/bash

# Trap script termination to ensure child processes are killed
trap 'kill $(jobs -p)' EXIT

# Start PostgreSQL in the background
sudo systemctl start postgresql
# Optional: wait a moment to ensure Postgres is up
sleep 2

# Run collectstatic
python3.13 -m poetry run mobilityshift/manage.py collectstatic --noinput

# Start the scheduler in the background
python3.13 -m poetry run mobilityshift/manage.py runapscheduler &
SCHEDULER_PID=$!

# Start Django (gunicorn) in the foreground
python3.13 -m poetry run ./gunicorn.sh

# When gunicorn exits, trap will kill the scheduler
# Stop PostgreSQL too
sudo systemctl stop postgresql
