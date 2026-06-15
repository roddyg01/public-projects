"""Packaging configuration for breachtl."""

from setuptools import find_packages, setup

with open("README.md", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="breachtl",
    version="0.1.0",
    description=(
        "Build a breach exposure timeline and analysis from Have I Been "
        "Pwned data."
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Rodrigo Garcia",
    url="https://github.com/YOUR_USERNAME/breach-timeline",
    packages=find_packages(exclude=["tests"]),
    install_requires=[],  # standard library only
    python_requires=">=3.9",
    entry_points={"console_scripts": ["breachtl=breachtl.cli:main"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Topic :: Security",
        "Environment :: Console",
    ],
)
