#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Setup script for OBDiag MCP Server
"""

from setuptools import setup, find_packages
import os


# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


# Read requirements from pyproject.toml
def get_requirements():
    requirements = []
    try:
        # tomllib is available in Python 3.11+
        import tomllib

        with open("pyproject.toml", "rb") as f:
            data = tomllib.load(f)
            requirements = data.get("project", {}).get("dependencies", [])
    except ImportError:
        # Fallback for Python 3.10
        try:
            import tomli as tomllib

            with open("pyproject.toml", "rb") as f:
                data = tomllib.load(f)
                requirements = data.get("project", {}).get("dependencies", [])
        except ImportError:
            # Manual fallback for Python 3.10
            requirements = [
                "fastmcp>=1.0",
                "uvicorn>=0.27.1",
            ]
    return requirements


setup(
    name="obdiag-mcp",
    version="0.0.3",
    description="OBDiag MCP Server - Model Context Protocol server for OceanBase Diagnostic Tool",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="OceanBase",
    author_email="support@oceanbase.com",
    url="https://github.com/oceanbase/mcp-oceanbase",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Database",
        "Topic :: System :: Monitoring",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords=[
        "oceanbase",
        "obdiag",
        "mcp",
        "diagnostic",
        "database",
        "monitoring",
    ],
    python_requires=">=3.10",
    install_requires=get_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.991",
            "build>=0.10.0",
            "twine>=4.0.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "obdiag-mcp=obdiag_mcp.server:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    project_urls={
        "Bug Reports": "https://github.com/oceanbase/mcp-oceanbase/issues",
        "Source": "https://github.com/oceanbase/mcp-oceanbase",
        "Documentation": "https://www.oceanbase.com/docs",
        "Community": "https://ask.oceanbase.com",
    },
)
