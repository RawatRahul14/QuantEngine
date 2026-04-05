# === Python Modules ===
import setuptools
from typing import List
from pathlib import Path

# === Function to Parse Requirements ===
def get_requirements(
    file_path: str
) -> List[str]:
    """
    This dynamically reads the requirements.txt file for the setup process
    """
    ## === Initiating the List ===
    requirements: List[str] = []

    ## === Opening and reading the file ===
    with open(
        Path(file_path),
    ) as f:
        requirements = f.readlines()

        ## === Removing white spaces, `-e .`, and empty strings ===
        requirements = [
            req.replace("\n", "").strip() 
            for req in requirements 
            if req.strip() and req.strip() != "-e ."
        ]

    return requirements

# === Reading the README file ===
with open(
    "README.md",
    "r",
    encoding = "utf-8"
) as f:
    long_description = f.read()

# === Package Versioning ===
__version__ = "0.0.1"

# === MetaData Configuration ===
REPO_NAME = "QuantEngine"
AUTHOR_USER_NAME = "RawatRahul14"
SRC_REPO = "QuantEngine"
AUTHOR_EMAIL = "rahulrawat272chd@gmail.com"

# === Package Setup Configuration ===
setuptools.setup(
    name = SRC_REPO,
    version = __version__,
    author = AUTHOR_USER_NAME,
    author_email = AUTHOR_EMAIL,
    description = "A comprehensive library for Options, Futures, and other Derivatives",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = f"https://github.com/{AUTHOR_USER_NAME}/{REPO_NAME}",
    
    ## === Project Links ===
    project_urls = {
        "Bug Tracker": f"https://github.com/{AUTHOR_USER_NAME}/{REPO_NAME}/issues",
        "Documentation": f"https://github.com/{AUTHOR_USER_NAME}/{REPO_NAME}#readme",
    },

    ## === PyPI Classifiers ===
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Office/Business :: Financial :: Investment :: Quantitative",
        "Intended Audience :: Financial Industry",
    ],

    ## === Package Directory Structure ===
    package_dir = {"": "src"},
    packages = setuptools.find_packages(where = "src"),

    ## === Requirements & Compatibility ===
    python_requires = ">=3.8",
    install_requires = get_requirements(
        file_path = "requirements.txt"
    )
)