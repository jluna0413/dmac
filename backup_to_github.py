"""
Backup the DMac project to GitHub.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

def run_command(command):
    """Run a shell command and return the output."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}")
        print(f"Error message: {e.stderr}")
        return None

def check_git_installed():
    """Check if Git is installed."""
    try:
        run_command("git --version")
        return True
    except Exception:
        print("❌ Git is not installed or not in the PATH.")
        print("Please install Git from: https://git-scm.com/downloads")
        return False

def check_git_repo():
    """Check if the current directory is a Git repository."""
    return os.path.exists(".git")

def initialize_git_repo():
    """Initialize a new Git repository."""
    print("Initializing Git repository...")
    run_command("git init")
    print("✅ Git repository initialized.")

def add_remote(remote_url):
    """Add a remote repository."""
    print(f"Adding remote repository: {remote_url}")
    run_command(f"git remote add origin {remote_url}")
    print("✅ Remote repository added.")

def check_remote_exists():
    """Check if a remote repository is configured."""
    remotes = run_command("git remote -v")
    return remotes and "origin" in remotes

def stage_files():
    """Stage all files for commit."""
    print("Staging files...")
    run_command("git add .")
    print("✅ Files staged.")

def commit_changes(message):
    """Commit the staged changes."""
    print(f"Committing changes with message: {message}")
    run_command(f'git commit -m "{message}"')
    print("✅ Changes committed.")

def push_to_remote(branch="main"):
    """Push the changes to the remote repository."""
    print(f"Pushing to remote repository (branch: {branch})...")
    run_command(f"git push -u origin {branch}")
    print("✅ Changes pushed to remote repository.")

def create_gitignore():
    """Create a .gitignore file if it doesn't exist."""
    if not os.path.exists(".gitignore"):
        print("Creating .gitignore file...")
        with open(".gitignore", "w") as f:
            f.write("""# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/
env/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Logs
logs/
*.log

# Local configuration
config/config.yaml
.env

# Ollama models
models/ollama/

# Learning data
models/learning_data/
models/feedback_data/

# Temporary files
.DS_Store
Thumbs.db
""")
        print("✅ .gitignore file created.")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Backup DMac to GitHub")
    parser.add_argument("--remote", help="GitHub repository URL (e.g., https://github.com/username/repo.git)")
    parser.add_argument("--message", default="Backup DMac project", help="Commit message")
    parser.add_argument("--branch", default="main", help="Branch name")
    args = parser.parse_args()
    
    # Check if Git is installed
    if not check_git_installed():
        sys.exit(1)
    
    # Create .gitignore file
    create_gitignore()
    
    # Check if the current directory is a Git repository
    if not check_git_repo():
        initialize_git_repo()
    
    # Check if a remote repository is configured
    if not check_remote_exists():
        if not args.remote:
            print("❌ No remote repository configured and no --remote argument provided.")
            print("Please provide a remote repository URL with --remote.")
            sys.exit(1)
        add_remote(args.remote)
    
    # Stage files
    stage_files()
    
    # Commit changes
    commit_changes(args.message)
    
    # Push to remote
    push_to_remote(args.branch)
    
    print("✅ DMac project successfully backed up to GitHub.")

if __name__ == "__main__":
    main()
