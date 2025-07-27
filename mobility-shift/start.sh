#!/bin/bash

# Trap script termination to ensure both child processes are killed
trap 'kill $(jobs -p)' EXIT

# Run collectstatic (non-interactive, no input prompt)
python3.13 -m poetry run mobilityshift/manage.py collectstatic --noinput

# Start the scheduler in the background
python3.13 -m poetry run mobilityshift/manage.py runapscheduler &
SCHEDULER_PID=$!

# Start the Django server (gunicorn) in the foreground
python3.13 -m poetry run ./gunicorn.sh

# When runserver exits, script will reach here and the trap will kill the scheduler
