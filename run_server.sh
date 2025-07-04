#!/bin/bash

# NetFix Django Project Runner
# This script activates the virtual environment and starts the Django development server

echo "Starting NetFix Django Application..."
echo "======================================="

# Check if virtual environment exists
if [ ! -d "netfix_env" ]; then
    echo "Error: Virtual environment 'netfix_env' not found!"
    echo "Please run the setup first."
    exit 1
fi

# Activate virtual environment
source netfix_env/bin/activate

# Check if Django is installed
if ! python -c "import django" 2>/dev/null; then
    echo "Error: Django is not installed in the virtual environment!"
    echo "Please install Django: pip install django"
    exit 1
fi

# Run Django checks
echo "Running Django system checks..."
python manage.py check

if [ $? -ne 0 ]; then
    echo "Error: Django system checks failed!"
    exit 1
fi

# Apply migrations if needed
echo "Applying database migrations..."
python manage.py migrate

# Start the development server
echo ""
echo "Starting Django development server..."
echo "The application will be available at: http://127.0.0.1:8000/"
echo "Press Ctrl+C to stop the server"
echo ""

python manage.py runserver
