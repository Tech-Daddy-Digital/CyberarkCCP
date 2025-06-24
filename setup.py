"""Setup script for CyberArk CCP API Python library."""
import os
from setuptools import setup, find_packages

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="cyberark-ccp",
    version="1.0.0",
    description="Official Python client for CyberArk Central Credential Provider (CCP) REST API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Kris Barrantes",
    author_email="kris.barrantes@cyberark.com",
    url="https://github.com/Tech-Daddy-Digital/CyberarkCCP",
    project_urls={
        "Bug Reports": "https://github.com/Tech-Daddy-Digital/CyberarkCCP/issues",
        "Documentation": "https://github.com/Tech-Daddy-Digital/CyberarkCCP/tree/main/docs",
        "Source": "https://github.com/Tech-Daddy-Digital/CyberarkCCP",
        "Changelog": "https://github.com/Tech-Daddy-Digital/CyberarkCCP/blob/main/CHANGELOG.md",
    },
    packages=find_packages(exclude=["test*", "docs*", "examples*"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration :: Authentication/Directory",
    ],
    keywords="cyberark ccp credential provider security authentication",
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-mock>=3.10.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "isort>=5.10.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
            "tox>=4.0.0",
            "types-requests",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "myst-parser>=0.18.0",
        ],
    },
    package_data={
        "cyberark_ccp": ["py.typed"],
    },
    zip_safe=False,
)