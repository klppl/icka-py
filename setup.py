#!/usr/bin/env python3
"""Setup script for icka."""

from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="icka",
    version="1.0.0",
    author="osm",
    description="IRCCloud Keep-Alive - Keeps your IRCCloud session alive",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/osm/icka",
    py_modules=["icka"],
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "icka=icka:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Communications :: Chat :: Internet Relay Chat",
    ],
    python_requires=">=3.6",
)

