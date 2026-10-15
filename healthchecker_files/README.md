# Server Health Monitor

A Python script that checks disk, CPU, and memory on Linux servers over SSH and emails you when something crosses a threshold.

## What it does

For each server in a JSON config file, it connects over SSH and checks:

- **Disk** — percent used on `/`
- **CPU** — 1-minute load average divided by core count
- **Memory** — percent of RAM used

Each value is compared to a threshold (defaults: disk 85%, CPU 80%, memory 85%). If any check fails, or the script can't connect, it sends an email alert for that server.

## Why it's useful

It needs nothing installed on the servers, only SSH access. For a few machines, that's lighter than setting up a full monitoring stack. Put it in cron and you get hourly checks.

## Requirements

- Python 3.7+
- paramiko (see `requirements.txt`)
- SSH key access to each server
- An SMTP account for alerts (for example, Gmail with an app password)

## How to run it

```bash
git clone https://github.com/roddyg01/public-projects.git
cd public-projects/healthchecker_files
pip install -r requirements.txt
cp config_example.json config.json
```

Edit `config.json` with your servers, thresholds, and email settings. `config.json` holds your SMTP password and is listed in `.gitignore`, so it won't be committed.

Set up SSH keys if you haven't:

```bash
ssh-keygen -t ed25519
ssh-copy-id user@server
```

For Gmail, turn on 2FA and create an app password in your Google account's security settings. Put that app password in `config.json`.

Run it:

```bash
python3 health_checker.py config.json
```

To run it every hour, add this to `crontab -e`:

```
0 * * * * /usr/bin/python3 /path/to/health_checker.py /path/to/config.json
```

## Example output

```
=== System Health Check - 2025-10-07 10:30:00.512843 ===

Checking Web Server (192.168.1.100)...
  ✓ disk: 45%
  ✓ cpu: 23.5%
  ✗ memory: 87%
  Alert sent to you@domain.com
```
