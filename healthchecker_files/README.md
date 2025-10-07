# Server Health Monitor

Python script for monitoring server health via SSH. Checks disk usage, CPU load, and memory usage. Sends email alerts when thresholds are exceeded.

## Features

- SSH-based monitoring (no agent required)
- Configurable thresholds
- Email alerts via SMTP
- Support for multiple servers
- Simple JSON configuration

## Requirements

- Python 3.7+
- SSH access to target servers
- SMTP server for alerts

## Installation
```bash
pip install -r requirements.txt
