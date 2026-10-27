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


def remove_unused_vcs_files() -> None:
    """Remove CI/CD files for the VCS that wasn't selected."""
    vcs = "{{ cookiecutter.vcs }}"
    if vcs == "github":
        gitlab_file = Path(".gitlab-ci.yml")
        if gitlab_file.exists():
            gitlab_file.unlink()
            print_success("Removed .gitlab-ci.yml (VCS=github)")
    elif vcs == "gitlab":
        github_dir = Path(".github")
        if github_dir.exists() and github_dir.is_dir():
            shutil.rmtree(github_dir)
            print_success("Removed .github/ (VCS=gitlab)")
    elif vcs == "none":
        gitlab_file = Path(".gitlab-ci.yml")
        github_dir = Path(".github")
        if gitlab_file.exists():
            gitlab_file.unlink()
            print_success("Removed .gitlab-ci.yml (VCS=none)")
        if github_dir.exists() and github_dir.is_dir():
            shutil.rmtree(github_dir)
            print_success("Removed .github/ (VCS=none)")


def generate_env_test() -> None:
    """
    Generate .env.test file based on required variables in settings.
    """
    print_info("Generating .env.test...")
    settings_files = []
    settings_dir = Path("config/settings")
    if settings_dir.exists() and settings_dir.is_dir():
        settings_files = list(settings_dir.glob("*.py"))
    elif Path("config/settings.py").exists():
        settings_files = [Path("config/settings.py")]

    env_example_path = Path(".env.example")
    env_test_path = Path(".env.test")

    if not settings_files:
        print_warning("No settings files found, skipping .env.test generation")
        return

    # 1. Identify required variables from settings files (config calls without defaults)
    import re
    required_vars = []
    for s_file in settings_files:
        with open(s_file, "r") as f:
            content = f.read()
            matches = re.finditer(r'config\(\s*["\']([^"\']+)["\']\s*(?:,[^)]*)?\)', content)
            for match in matches:
                full_call = match.group(0)
                var_name = match.group(1)
                if "default=" not in full_call and var_name not in required_vars:
                    required_vars.append(var_name)

    # 2. Extract values from .env.example if available
    example_values = {}
    if env_example_path.exists():
        with open(env_example_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and "=" in line and not line.startswith("#"):
                    key, val = line.split("=", 1)
                    example_values[key.strip()] = val.strip()

    # 3. Create .env.test
    with open(env_test_path, "w") as f:
        f.write("# Environment variables for testing\n")
        f.write("# Generated automatically from settings.py required variables\n\n")
        f.write("DEBUG=False\n")
        f.write("ALLOWED_HOSTS=localhost,127.0.0.1\n")
        
        # Override DATABASE_URL for testing if possible, or just use what's in example
        for var in required_vars:
            if var in ["DEBUG", "ALLOWED_HOSTS"]: continue
            
            val = example_values.get(var, "change-me")
            
            # Special logic for certain test Vars
            if var == "SECRET_KEY":
                val = "django-insecure-test-key-for-ci-logic-only"
            elif var == "DATABASE_URL":
                val = "sqlite:///data/test_db.sqlite3"
            
            f.write(f"{var}={val}\n")

    print_success(".env.test generated successfully")


def git_init() -> bool:
    """Initialize git repository."""
    print_info("Initializing git repository...")
    if not run_command("git init", "Failed to initialize git"):
        return False
    print_success("Git repository initialized")
    return True


def git_commit_initial() -> None:
    """Stage all generated files and create initial commit."""
    if run_command("git add .", "Failed to stage files"):
        run_command(
            'git commit -m "Initial commit from cookiecutter-django-lean template"',
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
    if run_command("uv sync --extra dev --extra test", "Failed to install dependencies"):
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
    
    print("6. Run the development server (runs Django + Huey worker):")
    print("   uv run python manage.py dev\n")
    
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
    remove_unused_vcs_files()
    git_init()
    create_env_file()
    generate_env_test()

    uv_success = setup_uv()

    if uv_success:
        setup_pre_commit()
        create_migrations()
        print_info("Formatting code with ruff...")
        run_command("uv run ruff check --fix .", "Failed to lint with ruff")
        run_command("uv run ruff format .", "Failed to format with ruff")
        print_success("Code formatted successfully")
    else:
        print_warning("Skipping pre-commit and migrations setup due to uv issues")

    git_commit_initial()
    print_next_steps()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print_error(f"Post-generation hook failed: {e}")
        sys.exit(1)
