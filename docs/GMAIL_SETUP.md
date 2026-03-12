# Gmail MCP Setup Guide

## Issue
Your Gmail OAuth token has expired and needs re-authentication.

---

## Step 1: Get Gmail API Credentials

### 1.1 Go to Google Cloud Console
https://console.cloud.google.com/

### 1.2 Create/Select Project
- Click the project dropdown at the top
- Click **NEW PROJECT** or select existing project
- Name it: "Gold Tier AI Employee" (or use existing)

### 1.3 Enable Gmail API
- In the sidebar, go to **APIs & Services** > **Library**
- Search for "Gmail API"
- Click on it and press **ENABLE**

### 1.4 Create OAuth Credentials
- Go to **APIs & Services** > **Credentials**
- Click **+ CREATE CREDENTIALS** > **OAuth client ID**
- Application type: **Desktop app**
- Name: "Gold Tier Gmail"
- Click **CREATE**

### 1.5 Download Credentials
- A download will start automatically (`credentials.json`)
- OR click the download icon next to your newly created credentials

### 1.6 Place Credentials File
- Create folder: `config/` in your project root
- Save the downloaded file as: `config/credentials.json`

Full path should be:
```
D:\Documents\GitHub\Personal_AI_Employee_Gold_Tier\config\credentials.json
```

---

## Step 2: Re-authenticate

### Option A: Automatic (Recommended)
```bash
cd D:\Documents\GitHub\Personal_AI_Employee_Gold_Tier
python watchers/gmail_reauth.py
```

This will:
1. Open browser for Google login
2. Ask you to grant permissions
3. Save the new token automatically

### Option B: Manual
Run the gmail watcher - it will prompt for authentication:
```bash
python watchers/gmail_watcher.py
```

---

## Step 3: Verify

After authentication, test it:
```bash
python watchers/gmail_watcher.py
```

You should see:
```
=======================================================
  GMAIL WATCHER - Silver Tier
  Checking every 120 seconds
  Query: is:unread is:important
  ...
✅ Gmail authenticated successfully!
```

---

## Troubleshooting

### Error: "Credentials file not found"
Make sure the file is at:
```
D:\Documents\GitHub\Personal_AI_Employee_Gold_Tier\config\credentials.json
```

### Error: "Token has been expired or revoked"
Delete the old token and re-authenticate:
```bash
python watchers/gmail_reauth.py
```

### Error: "Access blocked: This app's request is invalid"
- Make sure you selected **Desktop app** when creating OAuth credentials
- Make sure Gmail API is enabled
- Wait 5 minutes after creating credentials (propagation delay)

### Browser doesn't open automatically
- Copy the authorization URL from the console
- Paste it in your browser manually
- Complete the OAuth flow
- Copy the authorization code back to the terminal

---

## Required OAuth Scopes

The app requests these Gmail permissions:
- `gmail.readonly` - Read emails
- `gmail.send` - Send emails  
- `gmail.modify` - Mark as read/unread, label emails

These are required for full Gmail MCP functionality.

---

## Security Notes

- ✅ Credentials are stored locally in `config/`
- ✅ OAuth tokens are encrypted and stored in `config/token.json`
- ✅ Never commit `credentials.json` or `token.json` to Git (already in .gitignore)
- ✅ You can revoke access anytime from: https://myaccount.google.com/permissions

---

## Files Created

After setup, you'll have:
- `config/credentials.json` - OAuth client credentials (download from Google)
- `config/token.json` - Your authentication token (auto-generated)
- `watchers/gmail_reauth.py` - Re-authentication helper script

---

## Quick Commands

| Command | Purpose |
|---------|---------|
| `python watchers/gmail_reauth.py` | Force re-authentication |
| `python watchers/gmail_watcher.py` | Start Gmail watcher |
| Delete `config/token.json` | Reset authentication |

---

**Created:** 12 March 2026  
**Gold Tier AI Employee - Gmail Integration**
