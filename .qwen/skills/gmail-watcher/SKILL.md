# Gmail Watcher

Monitor Gmail for new important messages and create action files in the AI Employee vault.

## What this skill does

This skill enables autonomous Gmail monitoring by:
1. Connecting to Gmail API with OAuth2 credentials
2. Checking for unread/important messages at regular intervals
3. Creating structured action files in `Needs_Action/` folder
4. Tracking processed message IDs to avoid duplicates
5. Extracting key information (sender, subject, priority)

## When to use this skill

Use this skill when:
- You want 24/7 Gmail monitoring for your AI Employee
- New emails should trigger automated workflows
- You need to prioritize important client communications
- Email triage should happen automatically

## How it works

The watcher follows this pattern:
1. **Authenticate**: Use OAuth2 credentials to access Gmail
2. **Poll**: Check for unread messages every 2 minutes (configurable)
3. **Filter**: Identify important messages (keywords, senders)
4. **Create Action File**: Generate `.md` file in `Needs_Action/`
5. **Track**: Mark message as processed
6. **Notify**: Update Dashboard with new email count

## Setup Requirements

### 1. Enable Gmail API

```bash
# Go to Google Cloud Console
# 1. Create new project or select existing
# 2. Enable Gmail API
# 3. Create OAuth2 credentials
# 4. Download credentials.json to watchers/ folder
```

### 2. Install Dependencies

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

## Usage

```bash
# Start Gmail Watcher
python watchers/gmail_watcher.py start

# Check status
python watchers/gmail_watcher.py status

# Stop Watcher
python watchers/gmail_watcher.py stop

# Process emails once (dry run)
python watchers/gmail_watcher.py check --dry-run
```

## Action File Format

Created files follow this structure:

```markdown
---
type: email
from: client@example.com
subject: Urgent: Invoice Request
received: 2026-02-26T10:30:00Z
priority: high
status: pending
message_id: 18d4f2a3b5c6e7f8
---

## Email Content

[Email body text here]

## Suggested Actions
- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Archive after processing
```

## Priority Keywords

The watcher flags emails as high priority if they contain:
- `urgent`, `asap`, `immediate`
- `invoice`, `payment`, `billing`
- `client`, `project`, `deadline`
- `help`, `issue`, `problem`

## Safety Features

- **No Auto-Send**: Only reads emails, never sends without approval
- **Duplicate Prevention**: Tracks processed message IDs
- **Credential Security**: Uses OAuth2, never stores passwords
- **Rate Limiting**: Respects Gmail API quotas
- **Audit Logging**: All actions logged to `Logs/`

## Files Accessed

- `Needs_Action/EMAIL_*.md` (write)
- `Dashboard.md` (read/write)
- `Logs/gmail_watcher.log` (write)
- `~/.gmail_token.json` (read/write - OAuth token)

---
*Part of Silver Tier AI Employee - Gmail Integration*
