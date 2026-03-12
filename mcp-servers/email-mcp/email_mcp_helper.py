#!/usr/bin/env python
"""
Email MCP Helper - Send emails via Gmail API
Usage: python email_mcp_helper.py send_email <to> <subject> <body>
"""
import sys
import json
import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def send_email(to: str, subject: str, body: str):
    """Send email via Gmail API"""
    try:
        from gmail_watcher import GmailWatcher
        watcher = GmailWatcher('.')
        result = watcher.send_email(to, subject, body)
        print(json.dumps(result))
        if watcher.browser:
            watcher.browser.close()
        if hasattr(watcher, 'playwright'):
            watcher.playwright.stop()
    except Exception as e:
        print(json.dumps({'success': False, 'error': str(e)}))

if __name__ == '__main__':
    if len(sys.argv) < 5:
        print(json.dumps({'success': False, 'error': 'Usage: email_mcp_helper.py send_email <to> <subject> <body>'}))
        sys.exit(1)

    action = sys.argv[1]

    if action == 'send_email':
        send_email(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print(json.dumps({'success': False, 'error': f'Unknown action: {action}'}))
