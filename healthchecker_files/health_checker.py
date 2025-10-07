#!/usr/bin/env python3
"""
System Health Checker - SSH into servers and monitor resources
Usage: python health_checker.py config.json
"""

import paramiko
import json
import sys
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from typing import Dict, List

class HealthChecker:
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.thresholds = self.config.get('thresholds', {
            'disk': 85,
            'cpu': 80,
            'memory': 85
        })
        
    def ssh_execute(self, host: str, username: str, key_path: str, command: str) -> str:
        """Execute command via SSH and return output"""
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            client.connect(host, username=username, key_filename=key_path, timeout=10)
            stdin, stdout, stderr = client.exec_command(command)
            return stdout.read().decode().strip()
        finally:
            client.close()
    
    def check_disk(self, host: str, username: str, key_path: str) -> Dict:
        """Check disk usage"""
        cmd = "df -h / | awk 'NR==2 {print $5}'"
        result = self.ssh_execute(host, username, key_path, cmd)
        usage = int(result.replace('%', ''))
        
        return {
            'metric': 'disk',
            'value': usage,
            'unit': '%',
            'status': 'CRITICAL' if usage >= self.thresholds['disk'] else 'OK'
        }
    
    def check_cpu(self, host: str, username: str, key_path: str) -> Dict:
        """Check CPU usage (1-min load average relative to cores)"""
        cmd = "echo $(cat /proc/loadavg | awk '{print $1}') $(nproc)"
        result = self.ssh_execute(host, username, key_path, cmd)
        load, cores = result.split()
        cpu_percent = (float(load) / int(cores)) * 100
        
        return {
            'metric': 'cpu',
            'value': round(cpu_percent, 2),
            'unit': '%',
            'status': 'CRITICAL' if cpu_percent >= self.thresholds['cpu'] else 'OK'
        }
    
    def check_memory(self, host: str, username: str, key_path: str) -> Dict:
        """Check memory usage"""
        cmd = "free | awk 'NR==2 {printf \"%.0f\", ($3/$2)*100}'"
        result = self.ssh_execute(host, username, key_path, cmd)
        usage = int(result)
        
        return {
            'metric': 'memory',
            'value': usage,
            'unit': '%',
            'status': 'CRITICAL' if usage >= self.thresholds['memory'] else 'OK'
        }
    
    def check_server(self, server: Dict) -> List[Dict]:
        """Run all checks on a server"""
        results = []
        host = server['host']
        username = server['username']
        key_path = server.get('key_path', '~/.ssh/id_rsa')
        
        print(f"Checking {server['name']} ({host})...")
        
        try:
            results.append(self.check_disk(host, username, key_path))
            results.append(self.check_cpu(host, username, key_path))
            results.append(self.check_memory(host, username, key_path))
        except Exception as e:
            print(f"  ERROR: {e}")
            results.append({
                'metric': 'connection',
                'value': str(e),
                'status': 'ERROR'
            })
        
        return results
    
    def send_alert(self, server_name: str, issues: List[Dict]):
        """Send email alert for critical issues"""
        email_config = self.config.get('email')
        if not email_config:
            print("  No email config - skipping alert")
            return
        
        subject = f"[ALERT] System Health Issues on {server_name}"
        body = f"Critical issues detected on {server_name} at {datetime.now()}:\n\n"
        
        for issue in issues:
            body += f"- {issue['metric'].upper()}: {issue['value']}{issue.get('unit', '')}\n"
        
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = email_config['from']
        msg['To'] = email_config['to']
        
        try:
            with smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port']) as server:
                server.starttls()
                server.login(email_config['username'], email_config['password'])
                server.send_message(msg)
            print(f"  Alert sent to {email_config['to']}")
        except Exception as e:
            print(f"  Failed to send alert: {e}")
    
    def run(self):
        """Run health checks on all servers"""
        print(f"\n=== System Health Check - {datetime.now()} ===\n")
        
        for server in self.config['servers']:
            results = self.check_server(server)
            
            issues = [r for r in results if r['status'] in ['CRITICAL', 'ERROR']]
            
            for result in results:
                status_icon = '✓' if result['status'] == 'OK' else '✗'
                print(f"  {status_icon} {result['metric']}: {result['value']}{result.get('unit', '')}")
            
            if issues:
                self.send_alert(server['name'], issues)
            
            print()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python health_checker.py config.json")
        sys.exit(1)
    
    checker = HealthChecker(sys.argv[1])
    checker.run()
