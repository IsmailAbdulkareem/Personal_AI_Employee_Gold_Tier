#!/usr/bin/env python
"""
WhatsApp MCP Helper - Standalone script for MCP server
Usage: python whatsapp_mcp_helper.py <action> [args]
"""
import sys
import json
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from whatsapp_watcher import WhatsAppWatcher

def send_message(contact_name: str, message_text: str):
    """Send a WhatsApp message."""
    try:
        watcher = WhatsAppWatcher('.')
        result = watcher.send_message(contact_name, message_text)
        print(json.dumps(result))
        if watcher.browser:
            watcher.browser.close()
        if hasattr(watcher, 'playwright'):
            watcher.playwright.stop()
    except Exception as e:
        print(json.dumps({'success': False, 'error': str(e)}))

def reply_to_message(contact_name: str, reply_text: str, original_message: str = None):
    """Reply to a WhatsApp message."""
    try:
        watcher = WhatsAppWatcher('.')
        result = watcher.reply_to_message(contact_name, reply_text, original_message)
        print(json.dumps(result))
        if watcher.browser:
            watcher.browser.close()
        if hasattr(watcher, 'playwright'):
            watcher.playwright.stop()
    except Exception as e:
        print(json.dumps({'success': False, 'error': str(e)}))

def delete_message(contact_name: str, message_text: str, delete_for_everyone: bool = True):
    """Delete a WhatsApp message."""
    try:
        watcher = WhatsAppWatcher('.')
        result = watcher.delete_message(contact_name, message_text, delete_for_everyone)
        print(json.dumps(result))
        if watcher.browser:
            watcher.browser.close()
        if hasattr(watcher, 'playwright'):
            watcher.playwright.stop()
    except Exception as e:
        print(json.dumps({'success': False, 'error': str(e)}))

def mark_as_read(contact_name: str):
    """Mark WhatsApp chat as read."""
    try:
        watcher = WhatsAppWatcher('.')
        result = watcher.mark_as_read(contact_name)
        print(json.dumps(result))
        if watcher.browser:
            watcher.browser.close()
        if hasattr(watcher, 'playwright'):
            watcher.playwright.stop()
    except Exception as e:
        print(json.dumps({'success': False, 'error': str(e)}))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(json.dumps({'success': False, 'error': 'No action specified'}))
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == 'send_message':
        if len(sys.argv) < 4:
            print(json.dumps({'success': False, 'error': 'Missing arguments'}))
            sys.exit(1)
        send_message(sys.argv[2], sys.argv[3])
    
    elif action == 'reply_to_message':
        if len(sys.argv) < 4:
            print(json.dumps({'success': False, 'error': 'Missing arguments'}))
            sys.exit(1)
        original = sys.argv[4] if len(sys.argv) > 4 else None
        reply_to_message(sys.argv[2], sys.argv[3], original)
    
    elif action == 'delete_message':
        if len(sys.argv) < 4:
            print(json.dumps({'success': False, 'error': 'Missing arguments'}))
            sys.exit(1)
        delete_for = sys.argv[4].lower() == 'true' if len(sys.argv) > 4 else True
        delete_message(sys.argv[2], sys.argv[3], delete_for)
    
    elif action == 'mark_as_read':
        if len(sys.argv) < 3:
            print(json.dumps({'success': False, 'error': 'Missing contact name'}))
            sys.exit(1)
        mark_as_read(sys.argv[2])
    
    else:
        print(json.dumps({'success': False, 'error': f'Unknown action: {action}'}))
