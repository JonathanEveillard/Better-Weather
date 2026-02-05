import subprocess
import sys
import time
from pathlib  import Path
import os
import openmeteo.py


def verify_env():
    VENV_DIR = Path(__file__).parent / "venv"
    REQ_DIR = Path(__file__).parent / "requirements.txt"

    # Check if running inside virtual environment
    if sys.prefix != sys.base_prefix:
        print("Virtual environment detected. Installing requirements...")
        subprocess.run([sys.executable, "-m","pip","install","-r", str(REQ_DIR)], check=True)
        time.sleep(2)
        print("All packages are installed and up to date.")
    else:

        # Create virtual environment if none has been created yet
        if not VENV_DIR.exists():
            print("No virtual environment detected. Creating one...")
            subprocess.run([sys.executable, "-m", "venv", str(VENV_DIR)], check=True)
        
        time.sleep(2)
        print("Please run ./venv/Scripts/activate (Windows)\nsource ./venv/bin/activate (Linux/Mac) to activate the virtual environment.")

    return 

def run_program():
    subprocess.run([sys.executable, "openmeteo.py"], check=True)
    

if __name__ == "__main__":
    verify_env()
    run_program()
    