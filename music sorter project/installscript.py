import subprocess
import sys

def install_requirements():
    try:
        # Run pip install -r requirements.txt
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                                check=True, 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE, 
                                text=True)
        print("Installation successful!")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("An error occurred while installing packages.")
        print(e.stderr)

if __name__ == "__main__":
    install_requirements()