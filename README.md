# Chemical Equipment Parameter Visualizer

A hybrid web + desktop application for visualizing and analyzing chemical equipment data from CSV files. The application features a Django REST API backend, a React.js web frontend, and a PyQt5 desktop frontend.

## Project Structure

```
RAMI/
├── backend/                    # Django REST API backend
│   ├── chemical_equipment/    # Django project settings
│   ├── equipment/             # Equipment app (models, views, serializers)
│   ├── manage.py
│   └── requirements.txt
├── frontend-web/              # React.js web frontend
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── App.js
│   │   └── index.js
│   └── package.json
├── frontend-desktop/          # PyQt5 desktop frontend
│   ├── main.py
│   └── requirements.txt
├── sample_equipment_data.csv  # Sample CSV file for testing
└── README.md
```

## Features

- ✅ CSV file upload (Web & Desktop)
- ✅ Data parsing and storage with Pandas
- ✅ Summary statistics API (count, averages, type distribution)
- ✅ Interactive charts and visualizations
- ✅ History management (stores last 5 uploaded datasets)
- ✅ PDF report generation
- ✅ Basic authentication
- ✅ SQLite database for data persistence

## Tech Stack

### Backend
- **Django 4.2.7** - Web framework
- **Django REST Framework** - API development
- **Pandas** - CSV parsing and data analysis
- **ReportLab** - PDF generation
- **SQLite** - Database

### Frontend (Web)
- **React.js 18.2** - UI framework
- **Chart.js** - Data visualization
- **Axios** - HTTP client

### Frontend (Desktop)
- **PyQt5** - Desktop GUI framework
- **Matplotlib** - Data visualization
- **Requests** - HTTP client

## Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher and npm
- Git

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd RAMI
```

### 2. Backend Setup (Django)

#### Create and activate virtual environment (recommended)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Install dependencies

```bash
cd backend
pip install -r requirements.txt
```

#### Run migrations

```bash
python manage.py migrate
```

#### Create superuser (for admin access and API authentication)

```bash
python manage.py createsuperuser
```

Follow the prompts to create a user. For testing, you can use:
- Username: `admin`
- Password: `admin123`

#### Run the Django server

```bash
python manage.py runserver
```

The backend API will be available at `http://localhost:8000`

### 3. Web Frontend Setup (React)

#### Install dependencies

Open a new terminal window and navigate to the frontend-web directory:

```bash
cd frontend-web
npm install
```

#### Start the development server

```bash
npm start
```

The web application will open at `http://localhost:3000`

**Note:** The default credentials in the React app are:
- Username: `admin`
- Password: `admin123`

You can modify these in `frontend-web/src/App.js` if needed.

### 4. Desktop Frontend Setup (PyQt5)

#### Install dependencies

Open a new terminal window and navigate to the frontend-desktop directory:

```bash
cd frontend-desktop
pip install -r requirements.txt
```

#### Run the desktop application

```bash
python main.py
```

**Note:** The default credentials in the desktop app are:
- Username: `admin`
- Password: `admin123`

You can modify these in `frontend-desktop/main.py` if needed.

## Quick Start Guide

1. **Start the Backend:**
   ```bash
   cd backend
   python manage.py runserver
   ```
   Keep this terminal open. The API will run on `http://localhost:8000`

2. **Start the Web Frontend (in a new terminal):**
   ```bash
   cd frontend-web
   npm start
   ```
   The web app will open automatically at `http://localhost:3000`

3. **Start the Desktop Frontend (in a new terminal):**
   ```bash
   cd frontend-desktop
   python main.py
   ```

4. **Upload the sample CSV:**
   - Use the provided `sample_equipment_data.csv` file
   - Upload it through either interface
   - View the visualizations and data

## Usage

### CSV File Format

The CSV file should contain the following columns:
- `Equipment Name` - Name of the equipment
- `Type` - Type of equipment (e.g., Reactor, Pump, Compressor)
- `Flowrate` - Flowrate value (numeric)
- `Pressure` - Pressure value (numeric)
- `Temperature` - Temperature value (numeric)

A sample CSV file (`sample_equipment_data.csv`) is provided in the root directory.

### Web Application

1. Open `http://localhost:3000` in your browser
2. Click "Select CSV File" and choose a CSV file
3. Click "Upload" to upload the file
4. Select a dataset from the list to view its summary, charts, and data table
5. Click "Download PDF Report" to generate a PDF report

### Desktop Application

1. Run `python main.py` from the `frontend-desktop` directory
2. Enter your credentials (default: admin/admin123)
3. Click "Select CSV File" and choose a CSV file
4. Select a dataset from the list
5. View the data in the Summary, Charts, and Data Table tabs
6. Click "Download PDF Report" to generate a PDF report

## API Endpoints

All endpoints require basic authentication.

- `POST /api/upload/` - Upload CSV file
- `GET /api/datasets/` - List all datasets (last 5)
- `GET /api/datasets/<id>/summary/` - Get dataset summary statistics
- `GET /api/datasets/<id>/equipment/` - Get equipment list for a dataset
- `GET /api/datasets/<id>/pdf/` - Download PDF report

## Testing

1. Use the provided `sample_equipment_data.csv` file for testing
2. Upload it through either the web or desktop interface
3. Verify that:
   - Data is displayed correctly
   - Charts render properly
   - Summary statistics are accurate
   - PDF report can be downloaded

## Troubleshooting

### Backend Issues

- **Port already in use**: Change the port with `python manage.py runserver 8001`
- **Migration errors**: Run `python manage.py makemigrations` then `python manage.py migrate`
- **Authentication errors**: Make sure you've created a superuser and are using correct credentials

### Web Frontend Issues

- **Cannot connect to backend**: Ensure Django server is running on port 8000
- **CORS errors**: Check that `django-cors-headers` is installed and configured
- **Authentication errors**: Verify credentials in `App.js` match your Django superuser

### Desktop Frontend Issues

- **PyQt5 installation errors**: On some systems, you may need to install system dependencies
- **Cannot connect to backend**: Ensure Django server is running on port 8000
- **Chart display issues**: Ensure matplotlib is properly installed

## Development Notes

- The application stores only the last 5 uploaded datasets
- All data is stored in SQLite database (`backend/db.sqlite3`)
- PDF reports are generated on-demand
- Basic authentication is used for API security
- Default credentials (admin/admin123) are hardcoded for demo purposes - change in production

## Future Enhancements

- User registration and authentication
- More chart types and visualizations
- Export to Excel/CSV
- Real-time data updates
- Advanced filtering and search
- Multi-user support

## License

This project is created for intern screening purposes.

## Author

Developed as part of an intern screening task.
#
