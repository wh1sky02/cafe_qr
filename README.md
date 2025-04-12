# CafeQR - Smart Restaurant QR Code Ordering System

A modern, full-stack Django web application that enables restaurants to manage orders through QR codes. Customers can scan table QR codes to place orders, while staff can efficiently manage tables, menu items, and orders through an intuitive admin dashboard.

## 🌟 Features

### Customer Features
- **QR Code Scanning**: Scan table-specific QR codes to access the menu
- **Digital Menu**: Browse through categorized menu items with images and descriptions
- **Cart Management**: Add/remove items, adjust quantities
- **Order Tracking**: Real-time order status updates
- **Mobile-Friendly**: Responsive design for optimal mobile experience

### Admin Features
- **Dashboard**: Overview of orders, tables, and business metrics
- **QR Code Management**: Generate, regenerate, and manage QR codes for tables
- **Menu Management**: 
  - Add/edit/delete menu items
  - Organize items by categories
  - Set prices and descriptions
  - Upload item images
- **Table Management**: Add/remove tables, track table status
- **Order Management**: View and update order statuses
- **Transaction History**: Track and manage payment transactions

## 🛠️ Technology Stack

- **Backend**: Django 5.1.6
- **Frontend**: 
  - TailwindCSS
  - JavaScript (Vanilla)
- **Database**: SQLite (local)
- **Image Processing**: Pillow
- **QR Code Generation**: qrcode[pil]
- **Containerization**: Docker & Docker Compose

## 📋 Prerequisites

- Python 3.11+
- Docker and Docker Compose (for containerized deployment)
- Node.js and npm (for TailwindCSS)

## 🚀 Getting Started

### Local Development Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd cafeqr
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create .env file in the project root:
```env
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=db.sqlite3
DB_ENGINE=django.db.backends.sqlite3
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Start the development server:
```bash
python manage.py runserver
```

### Docker Deployment

1. Build and run with Docker Compose:
```bash
docker compose up --build
```

The application will be available at `http://localhost:8000`

## 📁 Project Structure

```
cafeqr/
├── cafe/                   # Main application
│   ├── static/            # Static files
│   ├── templates/         # HTML templates
│   ├── models.py          # Database models
│   └── views.py           # View logic
├── cafe_site/             # Project settings
├── media/                 # User-uploaded files
├── theme/                 # TailwindCSS config
├── docker-compose.yml     # Docker compose config
├── Dockerfile            # Docker configuration
└── requirements.txt      # Python dependencies
```

## 💾 Database Models

- **MenuItem**: Stores menu items with prices and categories
- **Category**: Menu item categories
- **Table**: Table information and QR code associations
- **Order**: Customer orders and their status
- **QRCode**: QR code data and associations
- **Cart**: Shopping cart implementation
- **Payment**: Transaction records

## 🔐 Security Features

- CSRF protection
- Secure password hashing
- Admin authentication
- Secure file uploads
- Environment variable configuration

## 🎨 UI/UX Features

- Modern, clean interface
- Responsive design
- Intuitive navigation
- Real-time updates
- Mobile-first approach

## 📱 Mobile Compatibility

The application is fully responsive and optimized for:
- iOS Safari
- Android Chrome
- Mobile Firefox
- Other mobile browsers

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Django framework
- TailwindCSS
- QR Code generation libraries
- Open-source community


## 🔄 Backup and Restore

The system includes backup functionality for:
- Menu items (menuitem_backup.json)
- Categories (category_backup.json)
- Database

To restore from backup:
```bash
python manage.py loaddata category_backup.json
python manage.py loaddata menuitem_backup.json
```
