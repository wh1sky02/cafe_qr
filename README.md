
# Cafe QR Code Ordering System

A Django-based web application for managing cafe orders through QR codes. The system allows customers to scan table QR codes, place orders, and helps staff manage tables and orders efficiently.

## Features

- QR Code based table management
- Digital menu with categories
- Cart functionality
- Online ordering system
- Admin dashboard for table management
- Responsive design using Tailwind CSS

## Tech Stack

- Django 5.1.6
- Tailwind CSS 3.8.0
- PostgreSQL Database
- Python 3.12
- Docker & Docker Compose

## Prerequisites

- Docker Desktop
- Git

## Getting Started

1. Clone the repository
2. Create a `.env` file in the cafe_project directory with:
```
SQL_NAME=cafe_db
SQL_USER=postgres
SQL_PASSWORD=your_password
```
3. Build and run the application:
```bash
cd cafe_project
docker compose up --build
```

The application will be available at http://0.0.0.0:8000

## Project Structure

```
cafe_project/
├── cafe/                 # Main application
│   ├── static/          # Static files (images, etc.)
│   ├── templates/       # HTML templates
│   ├── models.py        # Database models
│   └── views.py         # View functions
├── theme/               # Tailwind configuration
└── manage.py           # Django management script
```

## Models

- MenuItem: Stores menu items with prices and categories
- Table: Manages table information and status

## Admin Access

Access the admin panel at `/admin` to manage:
- Menu items
- Tables
- Orders

## License

MIT License
