#!/bin/bash
echo "Setting up Django Backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python create_superuser.py
echo ""
echo "To start the server, run:"
echo "cd backend"
echo "source venv/bin/activate"
echo "python manage.py runserver"
