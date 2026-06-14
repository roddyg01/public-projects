"""Packaging configuration for exifgeo."""

from setuptools import find_packages, setup

with open("README.md", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="exifgeo",
    version="0.1.0",
    description=(
        "Extract EXIF metadata and GPS coordinates from images and flag "
        "fields with privacy or operational-security implications."
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Rodrigo Garcia",
    url="https://github.com/roddyg01/exif-geo-osint",
    packages=find_packages(exclude=["tests"]),
    install_requires=["Pillow>=9.0"],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "exifgeo=exifgeo.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Topic :: Security",
        "Topic :: Utilities",
        "Environment :: Console",
    ],
)
