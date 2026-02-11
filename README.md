# Cookiecutter Django Lean

A modern, production-ready Django project template with sensible defaults and optional integrations.

[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/django-5.2-green.svg)](https://www.djangoproject.com/)
[![Cookiecutter](https://img.shields.io/badge/cookiecutter-2.6.0+-orange.svg)](https://github.com/cookiecutter/cookiecutter)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Philosophy

This template was created with a simple goal: **maintain Django's default project structure while providing the tools needed for production-grade applications**.

Unlike other templates that heavily restructure Django's layout, cookiecutter-django-lean respects Django's conventions and the familiar `django-admin startproject` structure. It adds modern tooling, optional integrations, and production best practices without forcing you to learn a new project organization.

Perfect for developers who want a clean starting point that feels like Django, not a framework on top of Django.

## Features

### Core Stack
- ✅ **Django 5.2** - Latest Django LTS
- ✅ **Python 3.12+** - Modern Python with type hints
- ✅ **UV Package Manager** - Lightning-fast dependency management
- ✅ **Daphne ASGI Server** - WebSocket support out of the box
- ✅ **Ruff** - Fast Python linter and formatter
- ✅ **Pre-commit Hooks** - Automated code quality checks
- ✅ **Pytest** - Modern testing with coverage and Factory Boy

### Optional Features
- 🔧 **Docker & Docker Compose** - Complete containerization with Nginx
- 🔧 **PostgreSQL or SQLite** - Choose your database
- 🔧 **Custom User Model** - Email-based authentication
- 🔧 **Django REST Framework** - API with JWT authentication
- 🔧 **Huey** - Background tasks (SQLite-backed, no Redis required)
- 🔧 **Mailpit** - Email testing in development
- 🔧 **Makefile** - Common Docker commands

## Quick Start

### Prerequisites

- Python 3.12+
- [Cookiecutter](https://github.com/cookiecutter/cookiecutter) (`pip install cookiecutter`)
- Docker (optional, for containerized development)

### Create a New Project

```bash
# Using cookiecutter
cookiecutter https://github.com/kiraboibrahim/cookiecutter-django-lean

# Or using cookiecutter with a local clone
git clone https://github.com/kiraboibrahim/cookiecutter-django-lean
cookiecutter cookiecutter-django-lean/
```

You'll be prompted for various configuration options (see [Configuration Options](#configuration-options) below).

### After Generation

```bash
cd your-project-name

# With Docker (recommended)
make build
make up
make migrate
make superuser

# Without Docker
cp .env.example .env
uv sync
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

## Configuration Options

During project generation, you'll be prompted for the following:

| Option | Description | Default | Choices |
|--------|-------------|---------|---------|
| `project_name` | Human-readable project name | My Django Project | - |
| `project_slug` | Project directory name | my_django_project | - |
| `project_description` | Short project description | A Django project | - |
| `author_name` | Your name | Your Name | - |
| `author_email` | Your email | your.email@example.com | - |
| `python_version` | Python version | 3.12 | - |
| `django_version` | Django version | 5.2 | - |
| `timezone` | Project timezone | UTC | - |
| `database` | Database backend | postgresql | postgresql, sqlite |
| `use_docker` | Include Docker support | yes | yes, no |
| `use_rest_framework` | Include Django REST Framework | yes | yes, no |
| `use_huey` | Include Huey for background tasks | yes | yes, no |
| `use_mailpit` | Include Mailpit for email testing | yes | yes, no |
| `include_accounts_app` | Include custom User model | yes | yes, no |

## What's Included

### Project Structure

```
your-project/
├── config/                    # Django settings and configuration
│   ├── settings.py           # Main settings with environment-based config
│   ├── urls.py               # Root URL configuration
│   ├── asgi.py               # ASGI application
│   └── wsgi.py               # WSGI application
├── accounts/                  # Custom user model (optional)
│   ├── models.py             # Email-based User model
│   ├── admin.py
│   └── tests/
├── .nginx/                    # Nginx configuration (if Docker enabled)
├── data/                      # Local data directory (SQLite, Huey)
├── Dockerfile                 # Multi-stage Docker build (if Docker enabled)
├── docker-compose.yml         # Service orchestration (if Docker enabled)
├── Makefile                   # Docker shortcuts (if Docker enabled)
├── entrypoint.sh             # Container startup script (if Docker enabled)
├── manage.py
├── pyproject.toml            # UV dependencies
├── .env.example              # Environment variable template
├── .pre-commit-config.yaml   # Pre-commit hooks configuration
└── README.md                 # Generated project documentation
```

### Docker Services (when enabled)

- **web** - Django application with Daphne (port 8000)
- **db** - PostgreSQL database (port 5432, if PostgreSQL selected)
- **nginx** - Reverse proxy for static/media files (port 1337, localhost only)
- **huey** - Background task worker (if Huey enabled)
- **mailpit** - Email testing interface (ports 8025/1025, if Mailpit enabled)

### Development Tools

- **Ruff** - Fast linting and formatting
- **Pre-commit** - Automated code quality checks on commit
- **Pytest** - Testing framework with coverage
- **Factory Boy** - Test fixture generation
- **Django Debug Toolbar** - Development debugging (optional)

### Configuration Management

- **python-decouple** - Environment variable management
- **dj-database-url** - Database URL parsing
- **Comprehensive .env.example** - All settings documented with defaults

## Features in Detail

### Docker Support

When Docker is enabled, you get:

- **Multi-stage Dockerfile** using UV for fast builds
- **docker-compose.yml** with all services configured
- **Makefile** with common commands (`make build`, `make up`, `make migrate`, etc.)
- **Health checks** for all services
- **Nginx** for static/media file serving
- **Localhost-only binding** for security

### Custom User Model

The optional accounts app provides:

- Email-based authentication (no username)
- Custom UserManager for user creation
- Pre-configured admin interface
- Ready for extension with additional fields

### REST API

When REST Framework is enabled:

- JWT authentication with dj-rest-auth
- CORS configuration (development and production)
- CSRF trusted origins configuration
- Token refresh endpoints

### Background Tasks

Huey integration provides:

- SQLite-backed task queue (no Redis required)
- Automatic worker in Docker
- Example task structure
- Results storage

### Email Testing

Mailpit integration provides:

- SMTP server for development
- Web UI at http://localhost:8025
- Email capture and inspection
- No external email service needed

### Testing

The testing setup includes:

- Pytest configuration
- Factory Boy for fixtures
- Coverage reporting
- In-memory SQLite for fast tests
- Fast password hashing for tests

## Best Practices

This template follows Django and Python best practices:

- ✅ Environment-based configuration (12-factor app)
- ✅ Separate settings for development/production
- ✅ Security settings enabled by default
- ✅ Type hints throughout
- ✅ Comprehensive documentation
- ✅ Automated code quality checks
- ✅ Health check endpoint
- ✅ Proper .gitignore and .dockerignore
- ✅ MIT License

## Customization

After generating your project, you can:

1. **Add Django apps**: Use `python manage.py startapp appname`
2. **Configure settings**: Edit `config/settings.py`
3. **Add dependencies**: Use `uv add package-name`
4. **Customize Docker**: Modify `Dockerfile` and `docker-compose.yml`
5. **Add pre-commit hooks**: Edit `.pre-commit-config.yaml`

## Examples

### Generate a minimal project

```bash
cookiecutter cookiecutter-django-lean/ \
  --no-input \
  project_name="My Blog" \
  database=sqlite \
  use_docker=no \
  use_rest_framework=no \
  use_huey=no
```

### Generate a full-featured API project

```bash
cookiecutter cookiecutter-django-lean/ \
  --no-input \
  project_name="My API" \
  database=postgresql \
  use_docker=yes \
  use_rest_framework=yes \
  use_huey=yes \
  use_mailpit=yes
```

## Troubleshooting

### Cookiecutter not found

```bash
pip install cookiecutter
```

### UV not available in generated project

```bash
pip install uv
```

### Docker issues

Make sure Docker and Docker Compose V2 are installed:

```bash
docker --version
docker compose version
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Update documentation
6. Submit a pull request

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Credits

Created and maintained by [Ibrahim Kirabo](https://github.com/kiraboibrahim)

Inspired by:
- [cookiecutter-django](https://github.com/cookiecutter/cookiecutter-django)
- [Django best practices](https://docs.djangoproject.com/)
- Modern Python tooling (UV, Ruff)

## Support

- 📖 [Documentation](https://github.com/kiraboibrahim/cookiecutter-django-lean/wiki)
- 🐛 [Issue Tracker](https://github.com/kiraboibrahim/cookiecutter-django-lean/issues)
- 💬 [Discussions](https://github.com/kiraboibrahim/cookiecutter-django-lean/discussions)

## Related Projects

- [Django](https://www.djangoproject.com/) - The web framework
- [Cookiecutter](https://github.com/cookiecutter/cookiecutter) - Project templating
- [UV](https://github.com/astral-sh/uv) - Fast Python package manager
- [Ruff](https://github.com/astral-sh/ruff) - Fast Python linter
