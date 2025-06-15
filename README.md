# FastAPI Question & PDF Management API

A FastAPI-based backend service for managing questions and PDF documents. This project provides a robust API for handling PDF files and question management with a clean, modern architecture.

## Features

- PDF file management and processing
- Question management system
- FastAPI-based REST API
- Development and production server configurations
- Project management utilities

## Prerequisites

- Python 3.8 or higher
- Virtual environment (automatically created by the setup script)

## Quick Start

1. Clone the repository:

```bash
git clone <repository-url>
cd db_backend
```

2. Run the setup script:

```bash
python manage.py setup
```

This will:

- Create a virtual environment
- Install all required dependencies
- Set up the project structure

## Project Management

The project includes a management script (`manage.py`) that provides several useful commands:

### Setup Commands

- `python manage.py setup` - Quick setup (creates venv, installs dependencies)

### Development Commands

- `python manage.py dev` - Start development server with auto-reload
- `python manage.py prod` - Start production server

### Testing & Quality

- `python manage.py clean` - Clean temporary files and cache

### Utilities

- `python manage.py status` - Show project status
- `python manage.py help` - Show help message

## Server Information

- Development server: Available at `http://localhost:8000`
- API documentation: Available at `http://localhost:8000/docs`
- Swagger UI: Available at `http://localhost:8000/docs`
- ReDoc: Available at `http://localhost:8000/redoc`

## Project Structure

```
db_backend/
├── app/                    # Application package
├── data/                   # Data directory
│   ├── pdfs/              # PDF files storage
│   └── questions.json     # Questions data
├── manage.py              # Project management script
├── requirements.txt       # Project dependencies
└── .env                  # Environment variables (not tracked in git)
```

## Configuration

The project uses environment variables for configuration. Create a `.env` file in the root directory with the following variables:

```env
API_HOST=localhost
API_PORT=8000
EXTERNAL_SERVICE_URL=<your-external-service-url>
EXTERNAL_SERVICE_TIMEOUT=30
```

## Development

1. Start the development server:

```bash
python manage.py dev
```

2. The server will automatically reload when you make changes to the code.

## Production

To run the server in production mode:

```bash
python manage.py prod
```

## Cleaning Up

To clean temporary files and cache:

```bash
python manage.py clean
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

## Support
