# MCP Servers for AI Employee

## Available MCP Servers

| Server | Description |
|--------|-------------|
| `email` | Gmail integration - Send emails, create drafts |
| `linkedin` | LinkedIn integration - Send messages, create posts, reply |

---

## Email MCP Server

Gmail integration for sending, reading, and managing emails.

### Installation

```bash
cd mcp-servers/email-mcp
npm install
```

### Configuration

The MCP server uses the same OAuth2 credentials as the Gmail Watcher:
- Credentials: `credentials.json` (project root)
- Token: `token.json` (project root)

### Required Gmail Scopes

The following scopes are configured in `watchers/gmail_watcher.py`:

```python
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",   # Read emails
    "https://www.googleapis.com/auth/gmail.send",       # Send emails
    "https://www.googleapis.com/auth/gmail.modify",     # Mark as read/unread, delete, archive
]
```

### Re-authenticate with New Scopes

To apply the new scopes, you need to re-authenticate:

```bash
# Delete the old token file
rm token.json

# Run the Gmail watcher to trigger OAuth consent
python watchers/gmail_watcher.py
```

This will open a browser window for you to grant the new permissions.

### Usage with Claude Code

Add to your Claude Code MCP configuration (`~/.claude-code-mcp.json` or project level):

```json
{
  "mcpServers": {
    "email": {
      "command": "node",
      "args": ["D:\\Documents\\GitHub\\Personal_AI_Employee_Bronze_Tier - Copy\\mcp-servers\\email-mcp\\index.js"],
      "env": {}
    }
  }
}
```

### Available Tools

#### send_email
Send an email via Gmail.

**Parameters:**
- `to` (required): Recipient email address
- `subject` (required): Email subject
- `body` (required): Email body text
- `cc` (optional): CC recipient

**Example:**
```
Use the email MCP server to send an email:
- to: client@example.com
- subject: Invoice #1234
- body: Dear Client, Please find attached...
```

#### create_draft_email
Create a draft email (safer alternative).

**Parameters:**
- Same as send_email

### Gmail Watcher Python Methods

The `GmailWatcher` class also provides these methods for direct Python usage:

```python
from watchers.gmail_watcher import GmailWatcher

watcher = GmailWatcher(vault_path="/path/to/project")

# Mark email as read
watcher.mark_as_read(message_id="abc123")

# Mark email as unread
watcher.mark_as_unread(message_id="abc123")

# Delete email permanently
watcher.delete_email(message_id="abc123")

# Archive email (remove from inbox)
watcher.archive_email(message_id="abc123")

# Send email
result = watcher.send_email(
    to="recipient@example.com",
    subject="Hello",
    body="This is the email body",
    cc="cc@example.com"  # optional
)

# Create draft
result = watcher.create_draft(
    to="recipient@example.com",
    subject="Hello",
    body="This is a draft"
)
```

### Safety Notes

1. **Always test with `create_draft_email` first**
2. **Verify the email content before sending**
3. **The Gmail Watcher and this MCP server share the same OAuth token**
4. **Revoke access in Google Account settings if needed**
5. **Deleted emails cannot be recovered**

## Troubleshooting

### "Token not found"
Run: `python watchers/gmail_watcher.py` to re-authenticate

### "Credentials not found"
Ensure `credentials.json` exists in the project root

### "npm install fails"
Ensure Node.js is installed: `node --version`

### "Insufficient permissions"
Delete `token.json` and re-run authentication to grant new scopes

---

## LinkedIn MCP Server

LinkedIn integration for sending messages, creating posts, and replying to conversations.

### Installation

```bash
cd mcp-servers/linkedin-mcp
npm install
```

### Configuration

The LinkedIn MCP server uses your existing browser session:
- Session: `watchers/.linkedin_session/` (created on first run)

### First Run - Login Required

The first time you use LinkedIn MCP, a browser window will open:
1. Browser opens automatically
2. Log in to LinkedIn manually
3. Session is saved for future runs
4. No repeated logins needed

### Usage with Qwen Code

The server is already configured in `.qwen-mcp.json`. Just ask naturally:

**Send a message:**
```
Send a LinkedIn message to John Doe saying "Hi John, great connecting with you!"
```

**Create a post:**
```
Create a LinkedIn post about our new AI Employee system launch
```

**Reply to a conversation:**
```
Reply to this LinkedIn message with "Thanks for reaching out, I'll get back to you soon"
```

### Available Tools

#### send_linkedin_message
Send a direct message to a LinkedIn connection.

**Parameters:**
- `recipient_name` (required): Name of the person to message
- `message` (required): Message content

**Example:**
```
Use send_linkedin_message:
- recipient_name: "John Doe"
- message: "Hi! Let's discuss the project..."
```

#### create_linkedin_post
Create a LinkedIn post on your feed.

**Parameters:**
- `content` (required): Post text content
- `image_path` (optional): Path to image to attach

**Example:**
```
Use create_linkedin_post:
- content: "Excited to announce our new AI project! #AI #Automation"
- image_path: "D:/images/launch.png"
```

#### reply_to_linkedin_message
Reply to the currently open LinkedIn conversation.

**Parameters:**
- `message` (required): Reply message content

**Example:**
```
Use reply_to_linkedin_message:
- message: "Thank you for your message. I'll respond shortly."
```

### Python Usage (Direct)

```python
from watchers.linkedin_watcher import LinkedInWatcher

watcher = LinkedInWatcher(vault_path=".", session_path=".linkedin_session")

# Send message
result = watcher.send_message("John Doe", "Hi! Let's connect...")

# Create post
result = watcher.create_post("New post content #hashtags")

# Reply to current conversation
result = watcher.reply_to_message("Thanks for reaching out!")
```

### Safety Notes

1. **Browser opens visibly** - You can see what's happening
2. **Session is persistent** - Login once, reused automatically
3. **LinkedIn ToS compliance** - Use responsibly, avoid spam
4. **Human oversight recommended** - Review before sending important messages

### Troubleshooting

#### "Session not found"
Run `python watchers/linkedin_watcher.py` once to create session

#### "Login required"
Complete manual login in the browser window when prompted

#### "Element not found" errors
LinkedIn may have updated selectors. Check browser window for visual errors.

#### "npm install fails"
Ensure Node.js is installed: `node --version`
