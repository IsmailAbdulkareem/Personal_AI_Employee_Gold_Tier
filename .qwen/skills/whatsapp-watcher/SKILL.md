# WhatsApp Watcher

Monitor WhatsApp Web for important messages and create action files in the AI Employee vault.

## What this skill does

This skill enables autonomous WhatsApp monitoring by:
1. Using Playwright to automate WhatsApp Web
2. Detecting unread messages with priority keywords
3. Creating structured action files in `Needs_Action/` folder
4. Maintaining session state for persistent login
5. Filtering messages by urgency and relevance

## When to use this skill

Use this skill when:
- You receive business-critical messages via WhatsApp
- Client communications happen on WhatsApp
- You need 24/7 message monitoring
- Quick response to urgent messages is required

## How it works

The watcher follows this pattern:
1. **Launch**: Start headless browser with saved session
2. **Connect**: Open WhatsApp Web and wait for connection
3. **Scan**: Check chat list for unread messages
4. **Filter**: Identify messages with priority keywords
5. **Create Action File**: Generate `.md` file in `Needs_Action/`
6. **Log**: Record all detected messages

## Setup Requirements

### 1. Install Playwright

```bash
pip install playwright
playwright install chromium
```

### 2. Initial QR Code Scan

```bash
python watchers/whatsapp_watcher.py auth
```

## Usage

```bash
# Start WhatsApp Watcher
python watchers/whatsapp_watcher.py start

# Check for new messages once
python watchers/whatsapp_watcher.py check

# Authenticate (QR code scan)
python watchers/whatsapp_watcher.py auth

# View status
python watchers/whatsapp_watcher.py status
```

## Priority Keywords

Messages flagged as high priority if they contain:
- `urgent`, `asap`, `immediate`, `quick`
- `invoice`, `payment`, `money`, `billing`
- `client`, `project`, `meeting`, `deadline`
- `help`, `issue`, `problem`, `error`
- `call`, `meeting`, `today`

## Safety & Privacy

- **Read-Only**: Only reads messages, never sends
- **Local Session**: Session stored locally, never uploaded
- **No Cloud**: All processing happens on your machine
- **Audit Logging**: All detections logged to `Logs/`

## Important Notes

WhatsApp automation may violate WhatsApp Terms of Service. Use at your own risk and consider:
- Using a business account
- Getting proper authorization
- Implementing rate limiting
- Not using for spam or bulk messaging

---
*Part of Silver Tier AI Employee - WhatsApp Integration*
