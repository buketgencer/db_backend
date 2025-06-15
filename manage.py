#!/usr/bin/env python3
"""
FastAPI Question & PDF Management API - Project Management Script
Usage: python manage.py <command>
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# Import configuration
from app.core.config import (
    API_HOST,
    API_PORT,
    EXTERNAL_SERVICE_URL,
    EXTERNAL_SERVICE_TIMEOUT,
)


class ProjectManager:
    def __init__(self):
        self.project_root = Path.cwd()
        self.venv_path = self.project_root / ".venv"
        self.app_module = "app.main:app"
        self.host = API_HOST
        self.port = API_PORT
        self.external_service_url = EXTERNAL_SERVICE_URL
        self.external_service_timeout = EXTERNAL_SERVICE_TIMEOUT

    def print_header(self, title):
        """Print formatted header"""
        print(f"\n{'='*50}")
        print(f"{title.center(50)}")
        print(f"{'='*50}\n")

    def run_command(self, command, check=True, shell=True):
        """Run shell command and return result"""
        try:
            if isinstance(command, list):
                result = subprocess.run(
                    command, check=check, shell=False, capture_output=True, text=True
                )
            else:
                result = subprocess.run(
                    command, check=check, shell=shell, capture_output=True, text=True
                )
            return result
        except subprocess.CalledProcessError as e:
            print(f"Error running command: {command}")
            print(f"Error: {e.stderr}")
            return None

    def check_python_version(self):
        """Check if Python version is suitable"""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print("Python 3.8+ is required")
            return False
        return True

    def create_venv(self):
        """Create virtual environment"""
        print("Creating virtual environment...")

        if self.venv_path.exists():
            print("Virtual environment already exists")
            return True

        result = self.run_command([sys.executable, "-m", "venv", str(self.venv_path)])
        if result and result.returncode == 0:
            print(f"Virtual environment created at {self.venv_path}")
            return True
        else:
            print("Failed to create virtual environment")
            return False

    def get_pip_command(self):
        """Get pip command for current environment"""
        if self.venv_path.exists():
            if os.name == "nt":  # Windows
                return str(self.venv_path / "Scripts" / "pip")
            else:  # Unix/Linux/Mac
                return str(self.venv_path / "bin" / "pip")
        return "pip"

    def get_python_command(self):
        """Get python command for current environment"""
        if self.venv_path.exists():
            if os.name == "nt":  # Windows
                return str(self.venv_path / "Scripts" / "python")
            else:  # Unix/Linux/Mac
                return str(self.venv_path / "bin" / "python")
        return "python"

    def install_dependencies(self):
        """Install project dependencies"""
        requirements_file = self.project_root / "requirements.txt"
        if not requirements_file.exists():
            print("requirements.txt not found")
            return False

        pip_cmd = self.get_pip_command()
        print("Installing dependencies...")

        result = self.run_command([pip_cmd, "install", "-r", str(requirements_file)])
        if result and result.returncode == 0:
            print("Dependencies installed successfully")
            return True
        else:
            print("Failed to install dependencies")
            return False

    def start_dev_server(self):
        """Start development server"""
        python_cmd = self.get_python_command()
        print("Starting development server...")
        print(f"Server will be available at http://{self.host}:{self.port}")
        print(f"API docs available at http://{self.host}:{self.port}/docs")

        cmd = [
            python_cmd,
            "-m",
            "uvicorn",
            self.app_module,
            "--reload",
            "--host",
            self.host,
            "--port",
            str(self.port),
        ]

        try:
            subprocess.run(cmd)
        except KeyboardInterrupt:
            print("\nServer stopped")

    def start_prod_server(self):
        """Start production server"""
        python_cmd = self.get_python_command()
        print("Starting production server...")

        cmd = [
            python_cmd,
            "-m",
            "uvicorn",
            self.app_module,
            "--host",
            self.host,
            "--port",
            str(self.port),
        ]

        try:
            subprocess.run(cmd)
        except KeyboardInterrupt:
            print("\nServer stopped")

    def clean_temp_files(self):
        """Clean temporary files and cache"""
        print("Cleaning temporary files...")

        patterns = [
            "**/__pycache__",
            "**/*.pyc",
            "**/*.pyo",
            "**/.pytest_cache",
            "**/.mypy_cache",
            "**/htmlcov",
            "**/*.egg-info",
        ]

        cleaned = 0
        for pattern in patterns:
            for path in self.project_root.glob(pattern):
                if path.is_file():
                    path.unlink()
                    cleaned += 1
                elif path.is_dir():
                    shutil.rmtree(path)
                    cleaned += 1

        print(f"Cleaned {cleaned} items")

    def show_status(self):
        """Show project status"""
        self.print_header("Project Status")

        # Check virtual environment
        venv_status = "✓ Exists" if self.venv_path.exists() else "✗ Not found"
        print(f"Virtual Environment: {venv_status}")

        # Check requirements
        req_status = (
            "✓ Found"
            if (self.project_root / "requirements.txt").exists()
            else "✗ Not found"
        )
        print(f"Requirements file: {req_status}")

        # Check app structure
        app_dir = self.project_root / "app"
        if app_dir.exists():
            print("App structure: ✓ Found")
        else:
            print("App structure: ✗ Not found")

        # Show configuration
        print("\nConfiguration:")
        print(f"  - API Host: {self.host}")
        print(f"  - API Port: {self.port}")
        print(f"  - External Service URL: {self.external_service_url}")
        print(f"  - External Service Timeout: {self.external_service_timeout}s")

    def quick_setup(self):
        """Quick setup: create venv, install deps"""
        self.print_header("Quick Setup")

        if not self.check_python_version():
            return False

        success = True
        success &= self.create_venv()
        success &= self.install_dependencies()

        if success:
            print("\nQuick setup completed successfully!")
        else:
            print("\nSetup failed")

        return success

    def show_help(self):
        """Show help message"""
        self.print_header("FastAPI Question & PDF Management API")

        print("Setup Commands:")
        print("  setup           Quick setup (create venv, install deps)")
        print("\nDevelopment Commands:")
        print("  dev             Start development server with auto-reload")
        print("  prod            Start production server")
        print("\nTesting & Quality:")
        print("  clean           Clean temporary files and cache")
        print("\nUtilities:")
        print("  status          Show project status")
        print("  help            Show this help message")


def main():
    manager = ProjectManager()

    if len(sys.argv) < 2:
        manager.show_help()
        return

    command = sys.argv[1].lower()

    command_map = {
        "setup": manager.quick_setup,
        "dev": manager.start_dev_server,
        "prod": manager.start_prod_server,
        "clean": manager.clean_temp_files,
        "status": manager.show_status,
        "help": manager.show_help,
    }

    if command in command_map:
        try:
            command_map[command]()
        except KeyboardInterrupt:
            print("\nOperation cancelled")
        except Exception as e:
            print(f"Error: {str(e)}")
    else:
        print(f"Unknown command: {command}")
        manager.show_help()


if __name__ == "__main__":
    main()
