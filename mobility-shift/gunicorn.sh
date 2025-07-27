#!/bin/bash

# Navigate to the project directory
cd "$(dirname "$0")/mobilityshift" || {
    echo "Failed to change directory to mobilityshift"
    exit 1
}

# Run gunicorn interactively with the specified WSGI module
exec gunicorn mobilityshift.wsgi

