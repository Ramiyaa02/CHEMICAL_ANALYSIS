@echo off
echo Setting up Django Backend...
cd backend
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python create_superuser.py
echo.
echo To start the server, run:
echo cd backend
echo venv\Scripts\activate
echo python manage.py runserver
pause
