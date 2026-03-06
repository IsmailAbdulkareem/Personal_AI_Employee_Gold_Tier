# Watchers - Silver Tier

Python watcher scripts for monitoring external channels.

## Watchers

| Script | Purpose | Interval |
|--------|---------|----------|
| `gmail_watcher.py` | Monitor Gmail for important emails | 2 minutes |
| `linkedin_watcher.py` | Monitor LinkedIn messaging for keywords | 1 minute |
| `whatsapp_watcher.py` | Monitor WhatsApp Web for priority messages | 30 seconds |
| `filesystem_watcher.py` | Monitor Inbox folder for file drops | 30 seconds |

## Usage

### Gmail Watcher
```bash
# Start monitoring
python watchers/gmail_watcher.py start

# Check once
python watchers/gmail_watcher.py check

# Authenticate (first time)
python watchers/gmail_watcher.py auth

# View status
python watchers/gmail_watcher.py status
```

### LinkedIn Watcher
```bash
# Start monitoring (opens browser, login once)
python watchers/linkedin_watcher.py

# Browser stays open - session saved for reuse
```

### WhatsApp Watcher
```bash
# Start monitoring
python watchers/whatsapp_watcher.py start

# Check once
python watchers/whatsapp_watcher.py check

# Authenticate (first time - QR scan)
python watchers/whatsapp_watcher.py auth

# View status
python watchers/whatsapp_watcher.py status
```

### File System Watcher
```bash
# Start monitoring
python watchers/filesystem_watcher.py
```

## Setup

### Gmail Setup
1. Create Google Cloud project
2. Enable Gmail API
3. Download `credentials.json` to project root
4. Run: `python watchers/gmail_watcher.py` (triggers OAuth)

### LinkedIn Setup
1. Ensure Playwright is installed: `pip install playwright`
2. Install browser: `playwright install chromium`
3. Run: `python watchers/linkedin_watcher.py`
4. Log in to LinkedIn manually in the browser window
5. Session saved in `.linkedin_session/`

### WhatsApp Setup
1. Ensure Playwright is installed: `pip install playwright`
2. Install browser: `playwright install chromium`
3. Run: `python watchers/whatsapp_watcher.py auth`

## Requirements

Install dependencies:
```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
pip install playwright
playwright install chromium
```

## LinkedIn Actions

### Send a Message
```python
from linkedin_watcher import LinkedInWatcher
watcher = LinkedInWatcher(".", ".linkedin_session")
watcher.send_message("John Doe", "Hi! Let's connect...")
```

### Create a Post
```python
watcher.create_post("Excited to share our new AI project! #AI #Automation")
```

### Reply to Message
```python
watcher.reply_to_message("Thanks for your message! I'll respond soon.")
```
