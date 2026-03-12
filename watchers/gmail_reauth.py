#!/usr/bin/env python
"""
Gmail Re-authentication Script
Run this to refresh your Gmail OAuth token.
"""

import os
import sys
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Config
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CREDENTIALS_FILE = PROJECT_ROOT / "config" / "credentials.json"
TOKEN_FILE = PROJECT_ROOT / "config" / "token.json"

# Full Gmail scopes
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
]

def reauthenticate():
    """Force re-authentication with Gmail."""
    print("=" * 60)
    print("  GMAIL RE-AUTHENTICATION")
    print("=" * 60)
    print()
    
    # Delete old token if exists
    if TOKEN_FILE.exists():
        print(f"🗑️  Removing old token: {TOKEN_FILE}")
        TOKEN_FILE.unlink()
        print("   Old token deleted.")
        print()
    
    # Check credentials file
    if not CREDENTIALS_FILE.exists():
        print(f"❌ ERROR: Credentials file not found: {CREDENTIALS_FILE}")
        print()
        print("Steps to get credentials:")
        print("1. Go to: https://console.cloud.google.com/")
        print("2. Select your project (or create new)")
        print("3. Enable Gmail API")
        print("4. Create OAuth 2.0 credentials (Desktop app)")
        print("5. Download the JSON file")
        print("6. Save as: config/credentials.json")
        print()
        return False
    
    print("✅ Credentials file found")
    print()
    
    # Start OAuth flow
    print("🔐 Starting OAuth authentication...")
    print()
    print("Instructions:")
    print("1. A browser window will open")
    print("2. Login with your Gmail account")
    print("3. Grant permissions to the app")
    print("4. You'll be redirected to a localhost page")
    print("5. Authentication will complete automatically")
    print()
    input("Press Enter to continue...")
    
    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            str(CREDENTIALS_FILE), 
            SCOPES,
            redirect_uri='urn:ietf:wg:oauth:2.0:oob'
        )
        
        auth_url, _ = flow.authorization_url(
            prompt='consent',
            access_type='offline',
            include_granted_scopes='true'
        )
        
        print()
        print("📋 Open this URL in your browser:")
        print("=" * 60)
        print(auth_url)
        print("=" * 60)
        print()
        
        auth_code = input("Enter the authorization code: ").strip()
        
        if not auth_code:
            print("❌ No authorization code entered")
            return False
        
        flow.fetch_token(code=auth_code)
        
        # Save token
        creds = flow.credentials
        TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
        
        print()
        print("✅ Authentication successful!")
        print(f"💾 Token saved to: {TOKEN_FILE}")
        print()
        print("You can now run: python watchers/gmail_watcher.py")
        print()
        
        # Show token info
        print("📊 Token Information:")
        print(f"   - Valid: {creds.valid}")
        print(f"   - Expired: {creds.expired}")
        print(f"   - Scopes: {len(creds.scopes)} permissions granted")
        if creds.expiry:
            print(f"   - Expires: {creds.expiry}")
        print()
        
        return True
        
    except Exception as e:
        print()
        print(f"❌ Authentication failed: {e}")
        print()
        print("Troubleshooting:")
        print("1. Make sure credentials.json is valid")
        print("2. Check that Gmail API is enabled in Google Cloud Console")
        print("3. Try again with a fresh credentials file")
        print()
        return False

if __name__ == "__main__":
    success = reauthenticate()
    sys.exit(0 if success else 1)
