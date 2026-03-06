#!/usr/bin/env python3
"""
Gmail Watcher Skill for AI Employee
Monitors Gmail for important messages and creates action files
"""
import sys
import os
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from email.utils import parseaddr
import argparse

# Try to import Google libraries
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

# Configuration
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
TOKEN_PATH = Path.home() / '.gmail_token.json'
CREDENTIALS_PATH = Path(__file__).parent.parent.parent.parent / 'watchers' / 'credentials.json'
CHECK_INTERVAL = 120  # seconds
LOG_FILE = Path(__file__).parent.parent.parent.parent / 'AI_Employee_Vault' / 'Logs' / 'gmail_watcher.log'

class GmailWatcher:
    """Monitor Gmail and create action files for new important messages"""
    
    def __init__(self, vault_path: str, check_interval: int = CHECK_INTERVAL):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.check_interval = check_interval
        self.processed_ids_file = Path(__file__).parent / 'processed_ids.json'
        self.running = False
        
        # Setup logging
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(LOG_FILE),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('GmailWatcher')
        
        # Load processed IDs
        self.processed_ids = self._load_processed_ids()
        
        # Priority keywords
        self.priority_keywords = [
            'urgent', 'asap', 'immediate', 'invoice', 'payment', 
            'billing', 'client', 'project', 'deadline', 'help', 
            'issue', 'problem', 'important'
        ]
        
        if not GOOGLE_AVAILABLE:
            self.logger.error("Google API libraries not installed. Run: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        
    def _load_processed_ids(self) -> set:
        """Load set of already processed message IDs"""
        if self.processed_ids_file.exists():
            try:
                with open(self.processed_ids_file, 'r') as f:
                    return set(json.load(f))
            except:
                return set()
        return set()
    
    def _save_processed_ids(self):
        """Save processed IDs to file"""
        # Keep only last 1000 IDs to prevent file growth
        ids_list = list(self.processed_ids)[-1000:]
        with open(self.processed_ids_file, 'w') as f:
            json.dump(ids_list, f)
    
    def authenticate(self):
        """Authenticate with Gmail API using OAuth2"""
        if not GOOGLE_AVAILABLE:
            self.logger.error("Cannot authenticate: Google libraries not available")
            return False
            
        creds = None
        
        # Load existing token
        if TOKEN_PATH.exists():
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        
        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not CREDENTIALS_PATH.exists():
                    self.logger.error(f"Credentials file not found: {CREDENTIALS_PATH}")
                    self.logger.info("Please download credentials.json from Google Cloud Console to watchers/ folder")
                    return False
                    
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save token
            TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(TOKEN_PATH, 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('gmail', 'v1', credentials=creds)
        self.logger.info("Successfully authenticated with Gmail")
        return True
    
    def check_for_updates(self) -> list:
        """Check for new unread important messages"""
        if not hasattr(self, 'service') or self.service is None:
            return []
        
        try:
            # Search for unread messages
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=10
            ).execute()
            
            messages = results.get('messages', [])
            new_messages = []
            
            for msg in messages:
                if msg['id'] not in self.processed_ids:
                    new_messages.append(msg)
            
            return new_messages
            
        except Exception as e:
            self.logger.error(f"Error checking Gmail: {e}")
            return []
    
    def get_message_details(self, message_id: str) -> dict:
        """Get full message details"""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            # Extract headers
            headers = message['payload'].get('headers', [])
            header_dict = {}
            for h in headers:
                header_dict[h['name']] = h['value']
            
            # Get body
            body = ""
            if 'parts' in message['payload']:
                for part in message['payload']['parts']:
                    if part['mimeType'] == 'text/plain' and 'body' in part:
                        import base64
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        break
            elif 'body' in message['payload']:
                import base64
                body = base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8')
            
            return {
                'id': message_id,
                'from': header_dict.get('From', 'Unknown'),
                'to': header_dict.get('To', ''),
                'subject': header_dict.get('Subject', 'No Subject'),
                'date': header_dict.get('Date', ''),
                'body': body,
                'snippet': message.get('snippet', '')
            }
            
        except Exception as e:
            self.logger.error(f"Error getting message {message_id}: {e}")
            return None
    
    def is_priority(self, message: dict) -> bool:
        """Check if message contains priority keywords"""
        text = f"{message.get('subject', '')} {message.get('snippet', '')}".lower()
        return any(keyword in text for keyword in self.priority_keywords)
    
    def create_action_file(self, message: dict) -> Path:
        """Create action file in Needs_Action folder"""
        priority = 'high' if self.is_priority(message) else 'medium'
        
        content = f"""---
type: email
from: {message['from']}
subject: {message['subject']}
received: {datetime.now().isoformat()}
priority: {priority}
status: pending
message_id: {message['id']}
---

## Email Content

**From:** {message['from']}  
**Subject:** {message['subject']}  
**Date:** {message['date']}

{message['body'] if message['body'] else message['snippet']}

## Suggested Actions
- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Archive after processing
"""
        
        # Create filename
        safe_subject = "".join(c if c.isalnum() else "_" for c in message['subject'][:30])
        filename = f"EMAIL_{message['id']}_{safe_subject}.md"
        filepath = self.needs_action / filename
        
        # Ensure directory exists
        self.needs_action.mkdir(parents=True, exist_ok=True)
        
        # Write file
        filepath.write_text(content, encoding='utf-8')
        self.processed_ids.add(message['id'])
        self._save_processed_ids()
        
        self.logger.info(f"Created action file: {filepath.name}")
        return filepath
    
    def update_dashboard(self, email_count: int):
        """Update dashboard with email stats"""
        dashboard_path = self.vault_path / 'Dashboard.md'
        
        if dashboard_path.exists():
            content = dashboard_path.read_text(encoding='utf-8')
            
            # Update email count (simple replacement)
            if 'New Emails:' in content:
                lines = content.split('\n')
                new_lines = []
                for line in lines:
                    if 'New Emails:' in line:
                        new_lines.append(f'- New Emails: {email_count}')
                    else:
                        new_lines.append(line)
                content = '\n'.join(new_lines)
            
            dashboard_path.write_text(content, encoding='utf-8')
    
    def run(self):
        """Main watcher loop"""
        self.logger.info("Starting Gmail Watcher")
        self.logger.info(f"Checking every {self.check_interval} seconds")
        
        if not self.authenticate():
            self.logger.error("Authentication failed. Exiting.")
            return
        
        self.running = True
        
        try:
            while self.running:
                try:
                    messages = self.check_for_updates()
                    
                    if messages:
                        self.logger.info(f"Found {len(messages)} new messages")
                        
                        for msg in messages:
                            details = self.get_message_details(msg['id'])
                            if details:
                                self.create_action_file(details)
                        
                        self.update_dashboard(len(messages))
                    
                    time.sleep(self.check_interval)
                    
                except KeyboardInterrupt:
                    self.logger.info("Stop requested by user")
                    break
                except Exception as e:
                    self.logger.error(f"Error in watcher loop: {e}")
                    time.sleep(self.check_interval)
                    
        finally:
            self.running = False
            self.logger.info("Gmail Watcher stopped")
    
    def stop(self):
        """Stop the watcher"""
        self.running = False


def main():
    parser = argparse.ArgumentParser(description='Gmail Watcher for AI Employee')
    parser.add_argument('command', choices=['start', 'stop', 'check', 'status', 'auth'],
                       help='Command to execute')
    parser.add_argument('--vault', default=None, help='Path to vault')
    parser.add_argument('--interval', type=int, default=CHECK_INTERVAL,
                       help='Check interval in seconds')
    parser.add_argument('--dry-run', action='store_true',
                       help='Check without creating files')
    
    args = parser.parse_args()
    
    # Get vault path
    if args.vault:
        vault_path = Path(args.vault)
    else:
        vault_path = Path(__file__).parent.parent.parent.parent / 'AI_Employee_Vault'
    
    watcher = GmailWatcher(str(vault_path), args.interval)
    
    if args.command == 'start':
        watcher.run()
    elif args.command == 'check':
        if watcher.authenticate():
            messages = watcher.check_for_updates()
            print(f"Found {len(messages)} new messages:")
            for msg in messages:
                details = watcher.get_message_details(msg['id'])
                if details:
                    priority = "HIGH" if watcher.is_priority(details) else "Normal"
                    print(f"  {priority}: {details['subject']} (from: {details['from']})")
            
            if not args.dry_run and messages:
                print(f"\nCreating {len(messages)} action files...")
                for msg in messages:
                    details = watcher.get_message_details(msg['id'])
                    if details:
                        watcher.create_action_file(details)
    elif args.command == 'auth':
        if watcher.authenticate():
            print("Authentication successful!")
        else:
            print("Authentication failed")
            sys.exit(1)
    elif args.command == 'status':
        print(f"Gmail Watcher Status:")
        print(f"  Vault: {vault_path}")
        print(f"  Processed IDs: {len(watcher.processed_ids)}")
        print(f"  Check Interval: {watcher.check_interval}s")
        print(f"  Log File: {LOG_FILE}")
    elif args.command == 'stop':
        print("Stop command received. If running, the watcher will stop.")
        print("Note: This only works if started from this script.")


if __name__ == '__main__':
    main()
