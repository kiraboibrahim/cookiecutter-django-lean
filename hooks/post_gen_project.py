"""
Post-generation hook for Django project template.

Performs automated setup tasks after the project is generated:
- Removes unselected apps and Docker files
- Initializes git repository
- Sets up Python environment with uv
- Creates .env file
- Installs pre-commit hooks
- Creates initial migrations

Exit codes:
    0: Post-generation setup completed successfully
    1: Critical error occurred during setup
"""
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Final

# Terminal colors
GREEN: Final[str] = "\033[92m"
YELLOW: Final[str] = "\033[93m"
BLUE: Final[str] = "\033[94m"
RED: Final[str] = "\033[91m"
RESET: Final[str] = "\033[0m"

# Cookiecutter variables
PROJECT_SLUG: Final[str] = "{{ cookiecutter.project_slug }}"
USE_DOCKER: Final[str] = "{{ cookiecutter.use_docker }}"
DATABASE: Final[str] = "{{ cookiecutter.database }}"
PYTHON_VERSION: Final[str] = "{{ cookiecutter.python_version }}"
INCLUDE_ACCOUNTS: Final[str] = "{{ cookiecutter.include_accounts_app }}"


def print_success(msg: str) -> None:
    """Print success message in green."""
    print(f"{GREEN}✓{RESET} {msg}")


def print_warning(msg: str) -> None:
    """Print warning message in yellow."""
    print(f"{YELLOW}⚠{RESET} {msg}")


def print_info(msg: str) -> None:
    """Print info message in blue."""
    print(f"{BLUE}ℹ{RESET} {msg}")


def print_error(msg: str) -> None:
    """Print error message in red."""
    print(f"{RED}✗{RESET} {msg}")


def run_command(cmd: str, error_msg: str = "Command failed") -> bool:
    """
    Execute a shell command and handle errors.
    
    Args:
        cmd: Shell command to execute
        error_msg: Error message to display if command fails
        
    Returns:
        True if command succeeded, False otherwise
    """
    try:
        subprocess.run(
            cmd,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"{error_msg}: {e.stderr}")
        return False


def remove_unselected_apps() -> None:
    """Remove app directories that weren't selected during generation."""
    apps_to_remove = []
    if INCLUDE_ACCOUNTS == "no":
        apps_to_remove.append("accounts")
    
    if not apps_to_remove:
        return
    
    print_info("Removing unselected apps...")
    for app in apps_to_remove:
        app_path = Path(app)
        if app_path.exists():
            shutil.rmtree(app_path)
            print_success(f"Removed {app}/")


def remove_docker_files() -> None:
    """Remove Docker-related files if Docker support not selected."""
    if USE_DOCKER == "yes":
        return
    
    print_info("Removing Docker files...")
    # Files to remove
    docker_files = ["Dockerfile", ".dockerignore", "docker-compose.yml", "entrypoint.sh", "Makefile"]
    for file in docker_files:
        file_path = Path(file)
        if file_path.exists():
            file_path.unlink()
            print_success(f"Removed {file}")
            
    # Directories to remove
    docker_dirs = [".nginx"]
    for directory in docker_dirs:
        dir_path = Path(directory)
        if dir_path.exists() and dir_path.is_dir():
            shutil.rmtree(dir_path)
            print_success(f"Removed {directory}/")


def initialize_git() -> None:
    """Initialize git repository with initial commit."""
    print_info("Initializing git repository...")
    if not run_command("git init", "Failed to initialize git"):
        return
    
    print_success("Git repository initialized")
    
    if run_command("git add .", "Failed to stage files"):
        run_command(
            'git commit -m "Initial commit from cookiecutter template"',
            "Failed to create initial commit"
        )
        print_success("Initial commit created")


def setup_uv() -> bool:
    """
    Set up Python environment using uv package manager.
    
    Returns:
        True if setup succeeded, False otherwise
    """
    print_info("Setting up Python environment with uv...")
    
    if not run_command("uv --version", "uv is not installed"):
        print_warning(
            "uv is not installed. Please install it with: pip install uv"
        )
        return False
    
    print_info(f"Pinning Python version to {PYTHON_VERSION}...")
    if run_command(
        f"uv python pin {PYTHON_VERSION}",
        f"Failed to pin Python {PYTHON_VERSION}"
    ):
        print_success(f"Python {PYTHON_VERSION} pinned (.python-version created)")
    
    print_info("Installing dependencies...")
    if run_command("uv sync", "Failed to install dependencies"):
        print_success("Dependencies installed successfully")
        return True
    return False


def create_env_file() -> None:
    """Create .env file from .env.example template if it doesn't exist."""
    print_info("Creating .env file...")
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if env_example.exists() and not env_file.exists():
        shutil.copy(env_example, env_file)
        print_success(".env file created from .env.example")
        print_warning("Please update .env with your actual configuration values")
    elif env_file.exists():
        print_warning(".env file already exists, skipping...")


def setup_pre_commit() -> None:
    """Install pre-commit git hooks for code quality checks."""
    print_info("Setting up pre-commit hooks...")
    if run_command("uv run pre-commit install", "Failed to install pre-commit hooks"):
        print_success("Pre-commit hooks installed")


def create_migrations() -> None:
    """Generate initial Django database migrations."""
    print_info("Creating initial migrations...")
    if run_command(
        "uv run python manage.py makemigrations",
        "Failed to create migrations"
    ):
        print_success("Initial migrations created")


def print_next_steps() -> None:
    """Display post-generation instructions and next steps."""
    print("\n" + "=" * 60)
    print(f"{GREEN}🎉 Project '{PROJECT_SLUG}' created successfully!{RESET}")
    print("=" * 60)
    print("\n📋 Next steps:\n")
    
    print("1. Navigate to your project:")
    print(f"   cd {PROJECT_SLUG}\n")
    
    print("2. Update your .env file with actual values:")
    print("   - SECRET_KEY (generate with: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')")
    print("   - DATABASE_URL")
    print("   - EMAIL settings\n")
    
    if DATABASE == "postgresql":
        print("3. Create your PostgreSQL database:")
        print(f"   createdb {PROJECT_SLUG}\n")
    
    print("4. Run migrations:")
    print("   uv run python manage.py migrate\n")
    
    print("5. Create a superuser:")
    print("   uv run python manage.py createsuperuser\n")
    
    print("6. Run the development server:")
    print("   uv run python manage.py runserver\n")
    
    print("7. Run tests:")
    print("   uv run pytest\n")
    
    if USE_DOCKER == "yes":
        print("8. Or use Docker:")
        print(f"   docker build -t {PROJECT_SLUG} .")
        print(f"   docker run -p 8000:8000 {PROJECT_SLUG}\n")
    
    print("📚 Documentation:")
    print("   - README.md - Project overview")
    print("   - pyproject.toml - Dependencies and configuration")
    print("   - .pre-commit-config.yaml - Code quality hooks\n")
    
    print(f"{GREEN}Happy coding! 🚀{RESET}\n")


def main() -> None:
    """Execute all post-generation setup tasks."""
    print(f"\n{BLUE}{'=' * 60}{RESET}")
    print(f"{BLUE}Post-generation setup for '{PROJECT_SLUG}'{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}\n")
    
    remove_unselected_apps()
    remove_docker_files()
    initialize_git()
    create_env_file()
    
    uv_success = setup_uv()
    
    if uv_success:
        setup_pre_commit()
        create_migrations()
    else:
        print_warning("Skipping pre-commit and migrations setup due to uv issues")
    
    print_next_steps()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print_error(f"Post-generation hook failed: {e}")
        sys.exit(1)
