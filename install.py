import platform
import os

requirements_path = os.path.join("requirements", "requirements_unix.txt")

if platform.system() == "Windows":
    requirements_path = os.path.join("requirements", "requirements_windows.txt")

os.system(f"python -m pip install -r {requirements_path}")
os.system(f"python setup.py install")
