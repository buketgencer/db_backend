#!/usr/bin/env python3
"""
FastAPI Question & PDF Management API - Project Management Script
Usage: python manage.py <command>
"""

import os
import sys
import subprocess
import shutil
import json
from datetime import datetime
from pathlib import Path

# Colors for terminal output
class Colors:
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    BLUE = '\033[0;34m'
    MAGENTA = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

class ProjectManager:
    def __init__(self):
        self.project_root = Path.cwd()
        self.venv_path = self.project_root / ".venv"
        self.data_dir = self.project_root / "data"
        self.pdf_dir = self.data_dir / "pdfs"
        self.questions_file = self.data_dir / "questions.json"
        self.requirements_file = self.project_root / "requirements.txt"
        
        # Configuration
        self.app_module = "main:app"
        self.host = "0.0.0.0"
        self.port = 8000

    def print_colored(self, message, color=Colors.NC):
        """Print colored message to terminal"""
        print(f"{color}{message}{Colors.NC}")

    def print_header(self, title):
        """Print formatted header"""
        print(f"\n{Colors.CYAN}{'='*50}{Colors.NC}")
        print(f"{Colors.CYAN}{title.center(50)}{Colors.NC}")
        print(f"{Colors.CYAN}{'='*50}{Colors.NC}\n")

    def run_command(self, command, check=True, shell=True):
        """Run shell command and return result"""
        try:
            if isinstance(command, list):
                result = subprocess.run(command, check=check, shell=False, capture_output=True, text=True)
            else:
                result = subprocess.run(command, check=check, shell=shell, capture_output=True, text=True)
            return result
        except subprocess.CalledProcessError as e:
            self.print_colored(f"Error running command: {command}", Colors.RED)
            self.print_colored(f"Error: {e.stderr}", Colors.RED)
            return None

    def check_python_version(self):
        """Check if Python version is suitable"""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            self.print_colored("Python 3.8+ is required", Colors.RED)
            return False
        return True

    def create_venv(self):
        """Create virtual environment"""
        self.print_colored("Creating virtual environment...", Colors.YELLOW)
        
        if self.venv_path.exists():
            self.print_colored("Virtual environment already exists", Colors.GREEN)
            return True
            
        result = self.run_command([sys.executable, "-m", "venv", str(self.venv_path)])
        if result and result.returncode == 0:
            self.print_colored(f"Virtual environment created at {self.venv_path}", Colors.GREEN)
            self.print_activation_message()
            return True
        else:
            self.print_colored("Failed to create virtual environment", Colors.RED)
            return False

    def print_activation_message(self):
        """Print virtual environment activation instructions"""
        if os.name == 'nt':  # Windows
            activate_cmd = f".\.venv\Scripts\Activate.ps1"
        else:  # Unix/Linux/Mac
            activate_cmd = f"source .venv/bin/activate"
        
        self.print_colored(f"To activate virtual environment: {activate_cmd}", Colors.BLUE)

    def get_pip_command(self):
        """Get pip command for current environment"""
        if self.venv_path.exists():
            if os.name == 'nt':  # Windows
                return str(self.venv_path / "Scripts" / "pip")
            else:  # Unix/Linux/Mac
                return str(self.venv_path / "bin" / "pip")
        return "pip"

    def get_python_command(self):
        """Get python command for current environment"""
        if self.venv_path.exists():
            if os.name == 'nt':  # Windows
                return str(self.venv_path / "Scripts" / "python")
            else:  # Unix/Linux/Mac
                return str(self.venv_path / "bin" / "python")
        return "python"

    def install_dependencies(self, dev=False):
        """Install project dependencies"""
        if not self.requirements_file.exists():
            self.print_colored("requirements.txt not found", Colors.RED)
            return False

        pip_cmd = self.get_pip_command()
        self.print_colored("Installing dependencies...", Colors.YELLOW)
        
        result = self.run_command([pip_cmd, "install", "-r", str(self.requirements_file)])
        if result and result.returncode == 0:
            self.print_colored("Dependencies installed successfully", Colors.GREEN)
            
            if dev:
                self.print_colored("Installing development dependencies...", Colors.YELLOW)
                dev_packages = ["pytest", "pytest-asyncio", "httpx", "black", "flake8", "mypy"]
                for package in dev_packages:
                    self.run_command([pip_cmd, "install", package])
                self.print_colored("Development dependencies installed", Colors.GREEN)
            
            return True
        else:
            self.print_colored("Failed to install dependencies", Colors.RED)
            return False

    def create_data_directories(self):
        """Create data directories and initialize files"""
        self.print_colored("Creating data directories...", Colors.YELLOW)
        
        # Create directories
        self.data_dir.mkdir(exist_ok=True)
        self.pdf_dir.mkdir(exist_ok=True)
        
        # Initialize questions.json if it doesn't exist
        if not self.questions_file.exists():
            with open(self.questions_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
        
        self.print_colored("Data directories created successfully", Colors.GREEN)
        return True

    def start_dev_server(self, debug=False):
        """Start development server"""
        self.create_data_directories()
        
        python_cmd = self.get_python_command()
        self.print_colored("Starting development server...", Colors.YELLOW)
        self.print_colored(f"Server will be available at http://{self.host}:{self.port}", Colors.GREEN)
        self.print_colored(f"API docs available at http://{self.host}:{self.port}/docs", Colors.GREEN)
        
        cmd = [python_cmd, "-m", "uvicorn", self.app_module, "--reload", "--host", self.host, "--port", str(self.port)]
        if debug:
            cmd.extend(["--log-level", "debug"])
        
        try:
            subprocess.run(cmd)
        except KeyboardInterrupt:
            self.print_colored("\nServer stopped", Colors.YELLOW)

    def start_prod_server(self, workers=1):
        """Start production server"""
        self.create_data_directories()
        
        python_cmd = self.get_python_command()
        self.print_colored(f"Starting production server with {workers} worker(s)...", Colors.YELLOW)
        
        cmd = [python_cmd, "-m", "uvicorn", self.app_module, "--host", self.host, "--port", str(self.port)]
        if workers > 1:
            cmd.extend(["--workers", str(workers)])
        
        try:
            subprocess.run(cmd)
        except KeyboardInterrupt:
            self.print_colored("\nServer stopped", Colors.YELLOW)

    def run_tests(self):
        """Run tests"""
        python_cmd = self.get_python_command()
        self.print_colored("Running tests...", Colors.YELLOW)
        
        result = self.run_command([python_cmd, "-m", "pytest", "-v"])
        if result and result.returncode == 0:
            self.print_colored("All tests passed!", Colors.GREEN)
        else:
            self.print_colored("Some tests failed", Colors.RED)

    def format_code(self):
        """Format code with black"""
        python_cmd = self.get_python_command()
        self.print_colored("Formatting code...", Colors.YELLOW)
        
        result = self.run_command([python_cmd, "-m", "black", ".", "--line-length=127"])
        if result and result.returncode == 0:
            self.print_colored("Code formatted successfully", Colors.GREEN)
        else:
            self.print_colored("Code formatting failed", Colors.RED)

    def lint_code(self):
        """Run linting"""
        python_cmd = self.get_python_command()
        self.print_colored("Running linter...", Colors.YELLOW)
        
        result = self.run_command([python_cmd, "-m", "flake8", ".", "--max-line-length=127"])
        if result and result.returncode == 0:
            self.print_colored("Linting passed", Colors.GREEN)
        else:
            self.print_colored("Linting issues found", Colors.YELLOW)
            if result:
                print(result.stdout)

    def backup_questions(self):
        """Backup questions file"""
        if not self.questions_file.exists():
            self.print_colored("No questions file found to backup", Colors.RED)
            return False
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.data_dir / f"questions_backup_{timestamp}.json"
        
        shutil.copy2(self.questions_file, backup_file)
        self.print_colored(f"Questions backed up to {backup_file.name}", Colors.GREEN)
        return True

    def list_backups(self):
        """List available backup files"""
        backup_files = list(self.data_dir.glob("questions_backup_*.json"))
        if not backup_files:
            self.print_colored("No backup files found", Colors.YELLOW)
            return []
        
        self.print_colored("Available backup files:", Colors.BLUE)
        for i, backup in enumerate(sorted(backup_files), 1):
            print(f"{i}. {backup.name}")
        
        return backup_files

    def restore_questions(self, backup_filename=None):
        """Restore questions from backup"""
        if not backup_filename:
            backups = self.list_backups()
            if not backups:
                return False
            
            try:
                choice = int(input("Enter backup number to restore: ")) - 1
                if 0 <= choice < len(backups):
                    backup_file = backups[choice]
                else:
                    self.print_colored("Invalid choice", Colors.RED)
                    return False
            except ValueError:
                self.print_colored("Invalid input", Colors.RED)
                return False
        else:
            backup_file = self.data_dir / backup_filename
            if not backup_file.exists():
                self.print_colored(f"Backup file {backup_filename} not found", Colors.RED)
                return False
        
        shutil.copy2(backup_file, self.questions_file)
        self.print_colored(f"Questions restored from {backup_file.name}", Colors.GREEN)
        return True

    def clean_temp_files(self):
        """Clean temporary files and cache"""
        self.print_colored("Cleaning temporary files...", Colors.YELLOW)
        
        patterns = [
            "**/__pycache__",
            "**/*.pyc",
            "**/*.pyo",
            "**/.pytest_cache",
            "**/.mypy_cache",
            "**/htmlcov",
            "**/*.egg-info"
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
        
        self.print_colored(f"Cleaned {cleaned} items", Colors.GREEN)

    def show_status(self):
        """Show project status"""
        self.print_header("Project Status")
        
        # Check virtual environment
        venv_status = "✓ Exists" if self.venv_path.exists() else "✗ Not found"
        print(f"Virtual Environment: {venv_status}")
        
        # Check requirements
        req_status = "✓ Found" if self.requirements_file.exists() else "✗ Not found"
        print(f"Requirements file: {req_status}")
        
        # Check data directories
        data_status = "✓ Exists" if self.data_dir.exists() else "✗ Not found"
        print(f"Data directory: {data_status}")
        
        # Check questions file
        if self.questions_file.exists():
            with open(self.questions_file, 'r', encoding='utf-8') as f:
                questions = json.load(f)
            print(f"Questions count: {len(questions)}")
        else:
            print("Questions file: ✗ Not found")
        
        # Check PDF files
        if self.pdf_dir.exists():
            pdf_files = list(self.pdf_dir.glob("*.pdf"))
            print(f"PDF files: {len(pdf_files)}")
        else:
            print("PDF directory: ✗ Not found")

    def quick_setup(self):
        """Quick setup: create venv, install deps, create data dirs"""
        self.print_header("Quick Setup")
        
        if not self.check_python_version():
            return False
        
        success = True
        success &= self.create_venv()
        success &= self.install_dependencies()
        success &= self.create_data_directories()
        
        if success:
            self.print_colored("\n🎉 Quick setup completed successfully!", Colors.GREEN)
            self.print_colored("\nNext steps:", Colors.BLUE)
            self.print_activation_message()
            self.print_colored("2. Run development server: python manage.py dev", Colors.BLUE)
        else:
            self.print_colored("\n❌ Setup failed", Colors.RED)
        
        return success

    def show_help(self):
        """Show help message"""
        self.print_header("FastAPI Question & PDF Management API")
        
        commands = {
            "Setup Commands": {
                "setup": "Quick setup (create venv, install deps, create data dirs)",
                "venv": "Create virtual environment",
                "install": "Install dependencies",
                "install-dev": "Install dependencies with dev packages",
                "data-dir": "Create data directories",
            },
            "Development Commands": {
                "dev": "Start development server with auto-reload",
                "dev-debug": "Start development server with debug logging",
                "prod": "Start production server",
                "prod-workers": "Start production server with multiple workers",
            },
            "Testing & Quality": {
                "test": "Run tests",
                "format": "Format code with black",
                "lint": "Run code linting",
                "clean": "Clean temporary files and cache",
            },
            "Data Management": {
                "backup": "Backup questions to timestamped file",
                "restore": "Restore questions from backup",
                "list-backups": "List available backup files",
            },
            "Utilities": {
                "status": "Show project status",
                "help": "Show this help message",
            }
        }
        
        for category, cmds in commands.items():
            self.print_colored(f"\n{category}:", Colors.YELLOW)
            for cmd, desc in cmds.items():
                print(f"  {Colors.GREEN}{cmd:<15}{Colors.NC} {desc}")

def main():
    manager = ProjectManager()
    
    if len(sys.argv) < 2:
        manager.show_help()
        return
    
    command = sys.argv[1].lower()
    
    command_map = {
        "setup": manager.quick_setup,
        "venv": manager.create_venv,
        "install": lambda: manager.install_dependencies(dev=False),
        "install-dev": lambda: manager.install_dependencies(dev=True),
        "data-dir": manager.create_data_directories,
        "dev": lambda: manager.start_dev_server(debug=False),
        "dev-debug": lambda: manager.start_dev_server(debug=True),
        "prod": lambda: manager.start_prod_server(workers=1),
        "prod-workers": lambda: manager.start_prod_server(workers=4),
        "test": manager.run_tests,
        "format": manager.format_code,
        "lint": manager.lint_code,
        "clean": manager.clean_temp_files,
        "backup": manager.backup_questions,
        "restore": manager.restore_questions,
        "list-backups": manager.list_backups,
        "status": manager.show_status,
        "help": manager.show_help,
    }
    
    if command in command_map:
        try:
            command_map[command]()
        except KeyboardInterrupt:
            manager.print_colored("\nOperation cancelled", Colors.YELLOW)
        except Exception as e:
            manager.print_colored(f"Error: {str(e)}", Colors.RED)
    else:
        manager.print_colored(f"Unknown command: {command}", Colors.RED)
        manager.show_help()

if __name__ == "__main__":
    main()