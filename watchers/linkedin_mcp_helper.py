#!/usr/bin/env python
"""
LinkedIn MCP Helper - Standalone script for MCP server
Usage: python linkedin_mcp_helper.py <action> [args]
"""
import sys
import json
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from linkedin_watcher import LinkedInWatcher

def send_message(recipient_name: str, message_text: str):
    """Send a LinkedIn message."""
    try:
        watcher = LinkedInWatcher('.', '.linkedin_session')
        result = watcher.send_message(recipient_name, message_text)
        print(json.dumps(result))
        watcher.close_browser()
    except Exception as e:
        print(json.dumps({'success': False, 'error': str(e)}))

def create_post(post_text: str, image_path: str = None):
    """Create a LinkedIn post."""
    try:
        watcher = LinkedInWatcher('.', '.linkedin_session')
        result = watcher.create_post(post_text, image_path)
        print(json.dumps(result))
        watcher.close_browser()
    except Exception as e:
        print(json.dumps({'success': False, 'error': str(e)}))

def reply_to_message(message_text: str):
    """Reply to a LinkedIn message."""
    try:
        watcher = LinkedInWatcher('.', '.linkedin_session')
        result = watcher.reply_to_message(message_text)
        print(json.dumps(result))
        watcher.close_browser()
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
    
    elif action == 'create_post':
        if len(sys.argv) < 3:
            print(json.dumps({'success': False, 'error': 'Missing content'}))
            sys.exit(1)
        image = sys.argv[3] if len(sys.argv) > 3 else None
        create_post(sys.argv[2], image)
    
    elif action == 'reply_to_message':
        if len(sys.argv) < 3:
            print(json.dumps({'success': False, 'error': 'Missing message'}))
            sys.exit(1)
        reply_to_message(sys.argv[2])
    
    else:
        print(json.dumps({'success': False, 'error': f'Unknown action: {action}'}))
