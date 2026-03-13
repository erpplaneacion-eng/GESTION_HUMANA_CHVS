# GEMINI.md - Sistema de Gestión Humana CAVJP

## Project Overview
**Sistema de Gestión Humana CAVJP** is a comprehensive Django-based web application for managing personnel records and recruitment processes. It allows candidates to register their personal, academic, and professional information autonomously, while providing administrators with tools to review, edit, and export this data.

### Main Technologies
- **Backend:** Django 5.2.7 (Python 3.13)
- **Database:** PostgreSQL (Production), SQLite (Development)
- **File Storage:** Cloudinary (for certificates and uploaded documents)
- **Email Service:** Gmail API (via OAuth2) for notifications and confirmation emails
- **Frontend:** Bootstrap 5, Font Awesome, jQuery
- **Deployment:** Railway.app
- **Key Libraries:** `openpyxl` & `pandas` (Excel reports), `ReportLab` (PDF generation), `whitenoise` (static files)

### Architecture
The project is structured into two main Django apps:
1. **`formapp`**: The core application handling public registrations, the admin dashboard, experience calculations, and reporting.
2. **`basedatosaquicali`**: Manages historical contract data imported from Excel, which is cross-referenced by ID (cédula) to enrich experience calculations.

---

## Building and Running

### Prerequisites
- Python 3.11+
- Virtual environment (`venv`)
- `.env` file with required credentials (see [Environment Variables](#environment-variables))

### Essential Commands

#### Local Development Setup
```bash
# Using the provided scripts
./start_local.sh          # Linux/Mac/WSL
start_local.bat           # Windows

# Manual Setup
cd gestion_humana
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r ../requirements.txt
python manage.py migrate
python manage.py runserver
```

#### Database & Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

#### Testing
```bash
python manage.py test formapp
```

#### Custom Management Commands
```bash
# Recalculate experience for all candidates
python manage.py recalcular_experiencias

# Recalculate for a specific ID with verbose output
python manage.py recalcular_experiencias --cedula 1234567890 --verbose
```

---

## Development Conventions

### Coding Style & Standards
- **Surgical Updates:** Always aim for precise, minimal changes that respect the existing architectural patterns.
- **Views Organization:** Views are modularized in `formapp/views/`:
    - `views_public.py`: Public forms and token-based updates.
    - `views_admin.py`: Candidate management (List, Detail, Edit, Delete).
    - `views_reports.py`: ZIP and Excel export logic.
- **Business Logic:** Core logic (like experience calculation and email sending) is centralized in `formapp/services.py`.
- **Validation:** File uploads must pass size (10MB), extension (PDF/JPG/PNG), and MIME type checks (defined in `formapp/validators.py`).

### Key Patterns
- **Experience Calculation:** Uses an interval-merging algorithm in `services.calcular_experiencia_total()` to combine local and historical data while eliminating overlaps.
- **Correction Flow:** Admins can trigger a "Correction Request," which generates a unique 48-hour token sent via email, allowing candidates to update their data without a full account.
- **Environment Detection:** `settings.py` automatically switches between SQLite and PostgreSQL based on the `DATABASE_URL` environment variable.

### Testing Practices
- **Comprehensive Coverage:** Tests should cover models, forms, views (especially the correction flow), and the experience calculation algorithm.
- **Location:** All tests are located in `formapp/tests/`.

---

## Environment Variables (.env)
The following variables are required for full functionality:
- `SECRET_KEY`: Django's secret key.
- `DEBUG`: Set to `True` for development, `False` for production.
- `DATABASE_URL`: Connection string for PostgreSQL (Production only).
- `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`: Cloudinary credentials.
- `GMAIL_TOKEN_JSON`: Full OAuth2 token JSON for Gmail API.
- `ADMIN_EMAIL`: Destination for admin notifications.
