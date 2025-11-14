#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Setup script for PowerMem MCP Server
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
                "powermem>=0.1.0",
                "fastmcp>=1.0",
                "uvicorn>=0.27.1",
            ]
    return requirements


setup(
    name="powermem-mcp",
    version="0.1.0",
    description="PowerMem MCP Server - Model Context Protocol server for PowerMem memory management",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="powermem Team",
    author_email="team@powermem.ai",
    url="https://github.com/oceanbase/powermem",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords=[
        "powermem",
        "mcp",
        "memory",
        "ai",
        "llm",
        "vector-database",
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
            "powermem-mcp=powermem_mcp.server:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    project_urls={
        "Bug Reports": "https://github.com/oceanbase/powermem/issues",
        "Source": "https://github.com/oceanbase/powermem",
        "Documentation": "https://powermem.ai/docs",
    },
)
