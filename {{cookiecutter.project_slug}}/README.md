# {{ cookiecutter.project_name }}

{{ cookiecutter.project_description }}

[![Python](https://img.shields.io/badge/python-{{ cookiecutter.python_version }}+-blue.svg)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/django-{{ cookiecutter.django_version }}-green.svg)](https://www.djangoproject.com/)
{%- if cookiecutter.use_rest_framework == "yes" %}
[![DRF](https://img.shields.io/badge/DRF-3.15+-red.svg)](https://www.django-rest-framework.org/)
{%- endif %}
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- ✅ Django {{ cookiecutter.django_version }} with Python {{ cookiecutter.python_version }}
{%- if cookiecutter.include_accounts_app == "yes" %}
- ✅ Custom User model with email-based authentication
{%- endif %}
{%- if cookiecutter.use_rest_framework == "yes" %}
- ✅ Django REST Framework with JWT authentication
- ✅ CORS configuration
{%- endif %}
- ✅ WebSocket support with Daphne ASGI server
- ✅ {{ cookiecutter.database|title }} database
{%- if cookiecutter.use_huey == "yes" %}
- ✅ Huey for background tasks (SQLite-backed)
{%- endif %}
{%- if cookiecutter.use_docker == "yes" %}
- ✅ Docker & Docker Compose support
- ✅ Nginx reverse proxy for static/media files
{%- if cookiecutter.use_mailpit == "yes" %}
- ✅ Mailpit for email testing
{%- endif %}
- ✅ Makefile for common Docker operations
{%- endif %}
- ✅ UV package manager for fast dependency management
- ✅ Ruff linting and formatting
- ✅ Pre-commit hooks for code quality
- ✅ Pytest with coverage and Factory Boy
- ✅ Health check endpoint at `/health/`

## Quick Start

{%- if cookiecutter.use_docker == "yes" %}

### With Docker (Recommended)

```bash
# 1. Clone and navigate to project
git clone <repository-url>
cd {{ cookiecutter.project_slug }}

# 2. Copy environment file
cp .env.example .env

# 3. Build and start services
make build
make up

# 4. Run migrations
make migrate

# 5. Create superuser
make superuser

# 6. Access the application
# Django: http://localhost:8000
# Admin: http://localhost:8000/admin
{%- if cookiecutter.use_mailpit == "yes" %}
# Mailpit: http://localhost:8025
{%- endif %}
# Nginx: http://localhost:1337
```

{%- endif %}

### Without Docker

```bash
# 1. Clone and navigate to project
git clone <repository-url>
cd {{ cookiecutter.project_slug }}

# 2. Install UV package manager
pip install uv

# 3. Copy and configure environment
cp .env.example .env
# Edit .env with your settings

{%- if cookiecutter.database == "postgresql" %}
# 4. Create database
createdb {{ cookiecutter.project_slug }}
{%- endif %}

# 5. Install dependencies
uv sync

# 6. Run migrations
uv run python manage.py migrate

# 7. Create superuser
uv run python manage.py createsuperuser

# 8. Run development server
uv run python manage.py runserver
```

## Prerequisites

{%- if cookiecutter.use_docker == "yes" %}

### With Docker
- Docker Engine 20.10+
- Docker Compose V2

### Without Docker
{%- endif %}
- Python {{ cookiecutter.python_version }}+
- UV package manager (`pip install uv`)
{%- if cookiecutter.database == "postgresql" %}
- PostgreSQL 14+
{%- endif %}

{%- if cookiecutter.use_docker == "yes" %}

## Docker Development

### Makefile Commands

The project includes a `Makefile` for common Docker operations:

```bash
make build          # Build Docker images
make up             # Start all services in background
make down           # Stop all services
make logs           # Follow logs from all services
make migrate        # Run database migrations
make makemigrations # Generate new migrations
make superuser      # Create Django superuser
make test           # Run tests
make shell          # Open Django shell
make bash           # Open bash shell in web container
```

### Services

The Docker Compose setup includes the following services:

{%- if cookiecutter.database == "postgresql" %}
- **db**: PostgreSQL {{ cookiecutter.database }} database
  - Port: `5432` (exposed to host)
{%- endif %}
- **web**: Django application with Daphne
  - Port: `8000` (exposed to host)
  - Health check: `http://localhost:8000/health/`
{%- if cookiecutter.use_huey == "yes" %}
- **huey**: Background task worker
{%- endif %}
- **nginx**: Reverse proxy for static/media files
  - Port: `1337` (bound to 127.0.0.1)
{%- if cookiecutter.use_mailpit == "yes" %}
- **mailpit**: Email testing interface
  - Web UI: `http://localhost:8025`
  - SMTP: `localhost:1025`
{%- endif %}

### Docker Compose Commands

```bash
# Start services
docker compose up -d

# View logs
docker compose logs -f web

# Execute commands in web container
docker compose exec web python manage.py shell

# Stop services
docker compose down

# Rebuild after dependency changes
docker compose build --no-cache
```

{%- endif %}

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

#### Django Core

```bash
# Generate a secure secret key
SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

#### Database

{%- if cookiecutter.database == "postgresql" %}
```bash
# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/{{ cookiecutter.project_slug }}

# Or with Docker
DATABASE_URL=postgresql://user:password@db:5432/{{ cookiecutter.project_slug }}
```
{%- else %}
```bash
# SQLite (default)
DATABASE_URL=sqlite:///data/db.sqlite3
```
{%- endif %}

#### Email

{%- if cookiecutter.use_mailpit == "yes" %}
```bash
# With Mailpit (Docker)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=mailpit
EMAIL_PORT=1025
EMAIL_USE_TLS=False
```
{%- else %}
```bash
# Console backend (development)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# SMTP (production)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-app-password
```
{%- endif %}

{%- if cookiecutter.use_rest_framework == "yes" %}

#### CORS & CSRF (Production)

```bash
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```
{%- endif %}

## Development

### Running Tests

```bash
{%- if cookiecutter.use_docker == "yes" %}
# With Docker
make test

# Or directly
docker compose exec web pytest
{%- endif %}

# Without Docker
uv run pytest

# With coverage
uv run pytest --cov=. --cov-report=html
open htmlcov/index.html
```

### Code Quality

```bash
# Run pre-commit hooks
uv run pre-commit run --all-files

# Lint with Ruff
uv run ruff check .

# Format with Ruff
uv run ruff format .

# Type checking (if mypy is installed)
uv run mypy .
```

{%- if cookiecutter.use_huey == "yes" %}

### Background Tasks with Huey

Huey is configured to use SQLite for task storage (no Redis required).

```python
# Example task in your_app/tasks.py
from huey.contrib.djhuey import task

@task()
def send_welcome_email(user_id):
    user = User.objects.get(id=user_id)
    send_mail(
        'Welcome!',
        f'Hello {user.email}',
        'from@example.com',
        [user.email],
    )
```

{%- if cookiecutter.use_docker == "yes" %}
The Huey worker runs automatically in Docker. To run manually:
{%- else %}
To run the Huey worker:
{%- endif %}

```bash
{%- if cookiecutter.use_docker == "yes" %}
# Check Huey logs
docker compose logs -f huey
{%- endif %}

# Run worker manually
uv run python manage.py run_huey
```
{%- endif %}

{%- if cookiecutter.use_mailpit == "yes" %}

### Email Testing with Mailpit

Mailpit captures all emails sent by the application:

1. Access Mailpit UI: http://localhost:8025
2. Send test email from Django shell:
   ```python
   from django.core.mail import send_mail
   send_mail('Test', 'Message', 'from@example.com', ['to@example.com'])
   ```
3. View the email in Mailpit interface
{%- endif %}

### Database Access

{%- if cookiecutter.database == "postgresql" %}
```bash
{%- if cookiecutter.use_docker == "yes" %}
# With Docker
docker compose exec db psql -U ${DB_USER} -d ${DB_NAME}
{%- endif %}

# Without Docker
psql -U user -d {{ cookiecutter.project_slug }}
```
{%- else %}
```bash
# SQLite
sqlite3 data/db.sqlite3
```
{%- endif %}

### Django Shell

```bash
{%- if cookiecutter.use_docker == "yes" %}
# With Docker
make shell
# or
docker compose exec web python manage.py shell
{%- endif %}

# Without Docker
uv run python manage.py shell
```

## Project Structure

```
{{ cookiecutter.project_slug }}/
├── config/                 # Django settings and configuration
│   ├── settings.py        # Main settings file
│   ├── urls.py            # Root URL configuration
│   ├── asgi.py            # ASGI application
│   └── wsgi.py            # WSGI application
{%- if cookiecutter.include_accounts_app == "yes" %}
├── accounts/              # Custom user model
│   ├── models.py          # User model with email authentication
│   ├── admin.py
│   └── tests/
{%- endif %}
{%- if cookiecutter.use_docker == "yes" %}
├── .nginx/                # Nginx configuration
│   └── nginx.conf
{%- endif %}
├── data/                  # Local data directory (SQLite, Huey)
{%- if cookiecutter.use_docker == "yes" %}
├── Dockerfile             # Multi-stage Docker build
├── docker-compose.yml     # Service orchestration
├── entrypoint.sh          # Container startup script
├── Makefile               # Docker command shortcuts
{%- endif %}
├── manage.py              # Django management script
├── pyproject.toml         # Python dependencies (UV)
├── .env.example           # Environment template
└── .pre-commit-config.yaml # Code quality hooks
```

## API Endpoints

{%- if cookiecutter.use_rest_framework == "yes" %}

### Authentication
- `POST /api/token/` - Obtain JWT token
- `POST /api/token/refresh/` - Refresh JWT token
{%- endif %}

### Health Check
- `GET /health/` - Application health status (returns "OK")

### Admin
- `/admin/` - Django admin interface

## Troubleshooting

### Common Issues

{%- if cookiecutter.use_docker == "yes" %}

**Port already in use**
```bash
# Find and kill process using port 8000
lsof -ti:8000 | xargs kill -9

# Or change port in docker-compose.yml
ports:
  - "8001:8000"  # Use port 8001 on host
```

**Database connection errors**
```bash
# Ensure database service is healthy
docker compose ps

# Check database logs
docker compose logs db

# Restart database service
docker compose restart db
```

**Permission errors with volumes**
```bash
# Fix ownership of data directory
sudo chown -R $USER:$USER data/
```
{%- endif %}

**Migration errors**
```bash
# Reset migrations (development only!)
{%- if cookiecutter.use_docker == "yes" %}
docker compose down -v  # Remove volumes
{%- endif %}
rm -rf */migrations/
uv run python manage.py makemigrations
uv run python manage.py migrate
```

**Pre-commit hook failures**
```bash
# Update pre-commit hooks
uv run pre-commit autoupdate

# Skip hooks temporarily (not recommended)
git commit --no-verify
```

## Deployment

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set strong `SECRET_KEY`
- [ ] Configure production database
- [ ] Set up static file serving (Nginx/CDN)
- [ ] Configure email backend
{%- if cookiecutter.use_rest_framework == "yes" %}
- [ ] Set CORS/CSRF trusted origins
{%- endif %}
- [ ] Enable HTTPS
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy

### Environment Variables Reference

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `SECRET_KEY` | Django secret key | Yes | - |
| `DEBUG` | Debug mode | Yes | `False` |
| `ALLOWED_HOSTS` | Allowed hosts (comma-separated) | Yes | - |
| `DATABASE_URL` | Database connection string | Yes | `sqlite:///data/db.sqlite3` |
| `EMAIL_BACKEND` | Email backend class | Yes | `console.EmailBackend` |
| `EMAIL_HOST` | SMTP server | No | - |
| `EMAIL_PORT` | SMTP port | No | `587` |
| `EMAIL_USE_TLS` | Use TLS | No | `True` |
| `EMAIL_HOST_USER` | SMTP username | No | - |
| `EMAIL_HOST_PASSWORD` | SMTP password | No | - |
{%- if cookiecutter.use_rest_framework == "yes" %}
| `CORS_ALLOWED_ORIGINS` | CORS origins (comma-separated) | No | - |
| `CSRF_TRUSTED_ORIGINS` | CSRF origins (comma-separated) | No | - |
{%- endif %}
{%- if cookiecutter.database == "postgresql" and cookiecutter.use_docker == "yes" %}
| `POSTGRES_PORT` | PostgreSQL host port | No | `5432` |
{%- endif %}

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

{{ cookiecutter.author_name }} <{{ cookiecutter.author_email }}>

## Support

For issues and questions:
- Create an issue on GitHub
- Check existing documentation
- Review Django documentation: https://docs.djangoproject.com/
