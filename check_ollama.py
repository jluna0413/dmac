"""
Check if Ollama is installed and running.
"""

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

def check_ollama_installed():
    """Check if Ollama is installed."""
    print("Checking if Ollama is installed...")

    try:
        # Try to run the ollama command
        version = run_command("ollama --version")
        if version:
            print(f"✅ Ollama is installed. Version: {version}")
            return True
        else:
            print("❌ Ollama is not installed or not in the PATH.")
            print("Please install Ollama from: https://ollama.com/download")
            return False
    except Exception as e:
        print(f"❌ Error checking Ollama installation: {e}")
        print("Please install Ollama from: https://ollama.com/download")
        return False

def check_ollama_running():
    """Check if Ollama server is running."""
    print("Checking if Ollama server is running...")

    try:
        # Try to list models
        models_output = run_command("ollama list")
        if models_output is not None:
            print("✅ Ollama server is running.")

            # Parse the models output
            models = [line.split()[0] for line in models_output.split('\n') if line.strip()]
            if models:
                print(f"Found {len(models)} models: {', '.join(models)}")
            else:
                print("No models found.")

            # Check for required models
            required_models = ["gemma3:12b", "GandalfBaum/deepseek_r1-claude3.7"]
            for model in required_models:
                if model in models:
                    print(f"✅ Required model '{model}' is available.")
                else:
                    print(f"❌ Required model '{model}' is not available.")
                    print(f"   Please pull it with: ollama pull {model}")

            return True
        else:
            print("❌ Ollama server is not running.")
            print("Please start Ollama with: ollama serve")
            return False
    except Exception as e:
        print(f"❌ Error checking Ollama server: {e}")
        print("Please start Ollama with: ollama serve")
        return False

def main():
    """Main function."""
    print("=== Ollama Check ===\n")

    # Check if Ollama is installed
    if not check_ollama_installed():
        sys.exit(1)

    # Check if Ollama server is running
    if not check_ollama_running():
        sys.exit(1)

    print("\n✅ Ollama is installed and running correctly.")
    print("You can now use DMac with local LLMs through Ollama.")

if __name__ == "__main__":
    main()
