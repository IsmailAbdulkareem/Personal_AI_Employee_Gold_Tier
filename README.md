# 🥇 AI Employee - Gold Tier

Autonomous AI Employee built with Qwen Code and Obsidian for managing communications, tasks, accounting, and social media across Gmail, WhatsApp, LinkedIn, Facebook, Instagram, and Twitter with full business automation.

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Gold Tier Features](#gold-tier-features)
- [Watchers Overview](#watchers-overview)
- [Architecture](#architecture)
- [Commands Reference](#commands-reference)
- [Project Structure](#project-structure)
- [Setup Guide](#setup-guide)
- [Gold Tier Upgrade Path](#gold-tier-upgrade-path)

---

## 🚀 Quick Start

### Process Tasks
```bash
# Process all files in Needs_Action (creates plans + approvals)
python orchestrator.py process
```

### Run Continuous Monitoring
```bash
# Orchestrator monitors all watchers and processes actions
python orchestrator.py run
```

### Check Status
```bash
python orchestrator.py status
```

### Start Ralph Wiggum Loop (Autonomous Tasks)
```bash
# Start autonomous task completion loop
python scripts/ralph_wiggum_loop.py "Process all pending tasks" --vault AI_Employee_Vault_Gold_Tier
```

### Generate Weekly Audit Report
```bash
# Generate weekly audit report
python scripts/audit_logger.py report --vault AI_Employee_Vault_Gold_Tier
```

---

## 🥇 Gold Tier Features

### ✅ All Silver Tier Features Plus:

| Feature | Status | Description |
|---------|--------|-------------|
| **Ralph Wiggum Loop** | 🟢 Ready | Autonomous multi-step task completion |
| **Enhanced Audit Logging** | 🟢 Ready | 90+ days retention, weekly reports |
| **Odoo Accounting** | 🟡 Planned | Full accounting integration via MCP |
| **Facebook Integration** | 🟡 Planned | Post messages, generate summaries |
| **Instagram Integration** | 🟡 Planned | Post content, analytics |
| **Twitter (X) Integration** | 🟡 Planned | Post tweets, generate summaries |
| **CEO Briefing** | 🟡 Planned | Weekly business audit with revenue metrics |
| **Financial Reconciliation** | 🟡 Planned | Auto-categorize transactions |

### New Gold Tier Commands

| Command | Description |
|---------|-------------|
| `python scripts/ralph_wiggum_loop.py "task"` | Start autonomous task loop |
| `python scripts/audit_logger.py report` | Generate weekly audit report |
| `python scripts/audit_logger.py query --type communication` | Query audit logs |
| `python scripts/ceo_briefing_generator.py` | Generate CEO briefing |
| `python scripts/weekly_audit.py` | Run weekly business audit |

---

## 👁️ Watchers Overview

All watchers follow the same pattern:
- **First Run**: Scans existing messages/chats and marks them as "already seen"
- **Monitoring**: Checks every 30-120 seconds for NEW messages
- **Action Files**: Creates `.md` files in `AI_Employee_Vault_Gold_Tier/Needs_Action/`

### Gmail Watcher

**Monitors:** Incoming emails with priority keywords

**Setup:**
```bash
# Authenticate Gmail (opens browser for OAuth)
python watchers/gmail_watcher.py auth
```

**Start Monitoring:**
```bash
# Start continuous monitoring
python watchers/gmail_watcher.py start

# Or use orchestrator
python orchestrator.py run
```

**Send Email:**
```bash
python watchers/email_mcp_helper.py send_message "recipient@example.com" "Subject" "Message body"
```

**Reply to Email:**
```bash
python watchers/email_mcp_helper.py reply "recipient@example.com" "Re: Subject" "Your reply"
```

**Check Status:**
```bash
python watchers/gmail_watcher.py status
```

---

### WhatsApp Watcher

**Monitors:** New WhatsApp messages with priority keywords

**Setup:**
```bash
# Authenticate WhatsApp (scan QR code with phone)
python watchers/whatsapp_watcher.py auth
```

**Start Monitoring:**
```bash
# Start continuous monitoring
python watchers/whatsapp_watcher.py start

# Or use orchestrator
python orchestrator.py run
```

**Send Message:**
```bash
python watchers/whatsapp_watcher.py send --contact "Contact Name" --message "Your message"
```

**Reply to Message:**
```bash
python watchers/whatsapp_watcher.py reply --contact "Contact Name" --message "Your reply"
```

**Mark as Read:**
```bash
python watchers/whatsapp_watcher.py mark-read --contact "Contact Name"
```

**Check Status:**
```bash
python watchers/whatsapp_watcher.py status
```

---

### LinkedIn Watcher

**Monitors:** LinkedIn messages and notifications

**Setup:**
```bash
# Authenticate LinkedIn (opens browser for login)
python watchers/linkedin_watcher.py auth
```

**Start Monitoring:**
```bash
# Start continuous monitoring
python watchers/linkedin_watcher.py start

# Or use orchestrator
python orchestrator.py run
```

**Send Message:**
```bash
python watchers/linkedin_mcp_helper.py send_message "Contact Name" "Your message"
```

**Reply to Message:**
```bash
python watchers/linkedin_mcp_helper.py reply "Contact Name" "Your reply"
```

**Post Content:**
```bash
python scripts/linkedin_poster.py post --type insight --vault AI_Employee_Vault_Gold_Tier
```

**Check Status:**
```bash
python watchers/linkedin_watcher.py status
```

---

### Facebook Watcher (Gold Tier)

**Monitors:** Facebook messages and notifications

**Setup:**
```bash
# Authenticate Facebook (OAuth flow)
python watchers/facebook_watcher.py auth
```

**Start Monitoring:**
```bash
python watchers/facebook_watcher.py start
```

**Post Content:**
```bash
python watchers/facebook_mcp_helper.py post_message "Your message"
```

**Check Status:**
```bash
python watchers/facebook_watcher.py status
```

---

### Instagram Watcher (Gold Tier)

**Monitors:** Instagram DMs and notifications

**Setup:**
```bash
# Authenticate Instagram
python watchers/instagram_watcher.py auth
```

**Start Monitoring:**
```bash
python watchers/instagram_watcher.py start
```

**Post Content:**
```bash
python watchers/instagram_mcp_helper.py post_media --image "path/to/image.jpg" --caption "Caption"
```

**Check Status:**
```bash
python watchers/instagram_watcher.py status
```

---

### Twitter/X Watcher (Gold Tier)

**Monitors:** Twitter DMs and mentions

**Setup:**
```bash
# Authenticate Twitter (OAuth 2.0)
python watchers/twitter_watcher.py auth
```

**Start Monitoring:**
```bash
python watchers/twitter_watcher.py start
```

**Post Tweet:**
```bash
python watchers/twitter_mcp_helper.py post_tweet "Your tweet content"
```

**Check Status:**
```bash
python watchers/twitter_watcher.py status
```

---

## 🏗️ Architecture

### Passive vs Active Scripts

**Watchers (Passive):**
- `*_watcher.py` files
- Monitor platforms every 30-120 seconds
- Create action files in `Needs_Action/`
- Don't send/modify anything
- First run registers existing messages without creating files

**MCP Helpers (Active):**
- `*_mcp_helper.py` files
- Called by approval workflow
- Actually send/post/delete content
- Execute approved actions only

### Gold Tier Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    GOLD TIER AI EMPLOYEE                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Gmail      │  │   WhatsApp   │  │   LinkedIn   │      │
│  │   Watcher    │  │   Watcher    │  │   Watcher    │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                 │               │
│         └─────────────────┼─────────────────┘               │
│                           │                                 │
│  ┌──────────────┐  ┌──────▼───────┐  ┌──────────────┐      │
│  │  Facebook    │  │  Needs_Action │  │   Instagram  │      │
│  │  Watcher     │  │    Folder     │  │   Watcher    │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                 │               │
│         └─────────────────┼─────────────────┘               │
│                           │                                 │
│  ┌──────────────┐  ┌──────▼─────────────────────────────┐  │
│  │   Twitter    │  │       Orchestrator                 │  │
│  │   Watcher    │  │  - Process tasks                   │  │
│  └──────────────┘  │  - Generate plans                  │  │
│                    │  - Manage approvals                │  │
│  ┌──────────────┐  │  - Ralph Wiggum Loop               │  │
│  │    Odoo      │  │  - Audit logging                   │  │
│  │   (Accounting)│  └──────┬─────────────────────────────┘  │
│  └──────┬───────┘         │                                 │
│         │                 │                                 │
│         └─────────────────┼─────────────────────────────────┘
│                           │                                 │
│              ┌────────────▼────────────┐                   │
│              │   Approval Workflow     │                   │
│              │   (Human-in-the-Loop)   │                   │
│              └────────────┬────────────┘                   │
│                           │                                 │
│         ┌─────────────────┼─────────────────┐              │
│         │                 │                 │              │
│  ┌──────▼───────┐  ┌──────▼───────┐  ┌──────▼───────┐     │
│  │  Email MCP   │  │  Social MCP  │  │  Odoo MCP    │     │
│  │   Server     │  │   Servers    │  │   Server     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Workflow

```
1. Watcher detects NEW message
   ↓
2. Creates action file in Needs_Action/
   ↓
3. Orchestrator processes file
   ↓
4. Creates plan in Plans/
   ↓
5. Creates approval request in Pending_Approval/
   ↓
6. User approves (adds ✅ in Obsidian)
   ↓
7. MCP helper executes approved action
   ↓
8. File moved to Done/
   ↓
9. Audit log updated
   ↓
10. Dashboard updated
```

### Ralph Wiggum Loop (Autonomous Tasks)

For multi-step tasks, the Ralph Wiggum pattern keeps Claude working until completion:

```
1. Orchestrator creates state file with task
   ↓
2. Claude works on task
   ↓
3. Claude tries to exit
   ↓
4. Stop hook checks: Is task in /Done?
   ↓
5. NO → Block exit, re-inject prompt (loop continues)
6. YES → Allow exit (task complete)
```

---

## 📚 Commands Reference

### Orchestrator Commands

| Command | Description |
|---------|-------------|
| `python orchestrator.py process` | Process all Needs_Action files |
| `python orchestrator.py run` | Run continuous monitoring mode |
| `python orchestrator.py status` | Check orchestrator status |

### Gmail Commands

| Command | Description |
|---------|-------------|
| `python watchers/gmail_watcher.py auth` | Authenticate Gmail |
| `python watchers/gmail_watcher.py start` | Start monitoring |
| `python watchers/gmail_watcher.py status` | Check status |
| `python watchers/email_mcp_helper.py send_message "to" "subject" "body"` | Send email |
| `python watchers/email_mcp_helper.py reply "to" "subject" "body"` | Reply to email |

### WhatsApp Commands

| Command | Description |
|---------|-------------|
| `python watchers/whatsapp_watcher.py auth` | Authenticate WhatsApp |
| `python watchers/whatsapp_watcher.py start` | Start monitoring |
| `python watchers/whatsapp_watcher.py status` | Check status |
| `python watchers/whatsapp_watcher.py send --contact "Name" --message "Text"` | Send message |
| `python watchers/whatsapp_watcher.py reply --contact "Name" --message "Text"` | Reply to message |
| `python watchers/whatsapp_watcher.py mark-read --contact "Name"` | Mark chat as read |

### LinkedIn Commands

| Command | Description |
|---------|-------------|
| `python watchers/linkedin_watcher.py auth` | Authenticate LinkedIn |
| `python watchers/linkedin_watcher.py start` | Start monitoring |
| `python watchers/linkedin_watcher.py status` | Check status |
| `python watchers/linkedin_mcp_helper.py send_message "Name" "Text"` | Send message |
| `python watchers/linkedin_mcp_helper.py reply "Name" "Text"` | Reply to message |
| `python scripts/linkedin_poster.py post --type insight` | Post content |

### Facebook Commands (Gold Tier)

| Command | Description |
|---------|-------------|
| `python watchers/facebook_watcher.py auth` | Authenticate Facebook |
| `python watchers/facebook_watcher.py start` | Start monitoring |
| `python watchers/facebook_watcher.py status` | Check status |
| `python watchers/facebook_mcp_helper.py post_message "Text"` | Post message |

### Instagram Commands (Gold Tier)

| Command | Description |
|---------|-------------|
| `python watchers/instagram_watcher.py auth` | Authenticate Instagram |
| `python watchers/instagram_watcher.py start` | Start monitoring |
| `python watchers/instagram_watcher.py status` | Check status |
| `python watchers/instagram_mcp_helper.py post_media --image "path" --caption "Text"` | Post media |

### Twitter/X Commands (Gold Tier)

| Command | Description |
|---------|-------------|
| `python watchers/twitter_watcher.py auth` | Authenticate Twitter |
| `python watchers/twitter_watcher.py start` | Start monitoring |
| `python watchers/twitter_watcher.py status` | Check status |
| `python watchers/twitter_mcp_helper.py post_tweet "Text"` | Post tweet |

### Odoo Accounting Commands (Gold Tier)

| Command | Description |
|---------|-------------|
| `python mcp-servers/odoo-mcp/auth.py` | Authenticate Odoo |
| `python mcp-servers/odoo-mcp/create_invoice.py` | Create invoice |
| `python mcp-servers/odoo-mcp/record_payment.py` | Record payment |
| `python mcp-servers/odoo-mcp/generate_report.py` | Generate financial report |

### Approval Workflow

| Command | Description |
|---------|-------------|
| `python scripts/approval_workflow_enhanced.py check` | Check pending approvals |
| `python scripts/approval_workflow_enhanced.py execute` | Execute approved actions |

### Ralph Wiggum Loop (Gold Tier)

| Command | Description |
|---------|-------------|
| `python scripts/ralph_wiggum_loop.py "task"` | Start autonomous task loop |
| `python scripts/ralph_wiggum_loop.py "task" --max-iterations 20` | Custom max iterations |

### Audit Logging (Gold Tier)

| Command | Description |
|---------|-------------|
| `python scripts/audit_logger.py log --type communication --action email_sent` | Log event |
| `python scripts/audit_logger.py query --start-date 2026-03-01` | Query events |
| `python scripts/audit_logger.py report` | Generate weekly report |
| `python scripts/audit_logger.py cleanup` | Clean up old logs |

### CEO Briefing (Gold Tier)

| Command | Description |
|---------|-------------|
| `python scripts/ceo_briefing_generator.py` | Generate CEO briefing |
| `python scripts/weekly_audit.py` | Run weekly business audit |

---

## 📁 Project Structure

```
Personal_AI_Employee_Gold_Tier/
├── config/                      # Configuration files
│   ├── credentials.json         # Gmail OAuth (git-ignored)
│   ├── token.json               # Gmail token (git-ignored)
│   ├── odoo_config.json         # Odoo config (git-ignored)
│   ├── facebook_config.json     # Facebook config (git-ignored)
│   ├── instagram_config.json    # Instagram config (git-ignored)
│   ├── twitter_config.json      # Twitter config (git-ignored)
│   └── .qwen-mcp.json           # MCP server config (git-ignored)
│
├── libs/                        # Node.js libraries
│   └── node_modules/            # Google APIs, etc.
│
├── watchers/                    # Watcher scripts
│   ├── base_watcher.py          # Base class for all watchers
│   ├── gmail_watcher.py         # Monitors Gmail (PASSIVE)
│   ├── email_mcp_helper.py      # Sends emails (ACTIVE)
│   ├── linkedin_watcher.py      # Monitors LinkedIn (PASSIVE)
│   ├── linkedin_mcp_helper.py   # Posts/messages (ACTIVE)
│   ├── whatsapp_watcher.py      # Monitors WhatsApp (PASSIVE)
│   ├── whatsapp_mcp_helper.py   # Sends messages (ACTIVE)
│   ├── facebook_watcher.py      # Monitors Facebook (PASSIVE) [Gold]
│   ├── facebook_mcp_helper.py   # Posts messages (ACTIVE) [Gold]
│   ├── instagram_watcher.py     # Monitors Instagram (PASSIVE) [Gold]
│   ├── instagram_mcp_helper.py  # Posts media (ACTIVE) [Gold]
│   ├── twitter_watcher.py       # Monitors Twitter (PASSIVE) [Gold]
│   ├── twitter_mcp_helper.py    # Posts tweets (ACTIVE) [Gold]
│   └── filesystem_watcher.py    # Monitors file drops
│
├── scripts/                     # Automation scripts
│   ├── plan_generator.py
│   ├── approval_workflow_enhanced.py
│   ├── ralph_wiggum_loop.py     # Autonomous task loop [Gold]
│   ├── audit_logger.py          # Enhanced audit logging [Gold]
│   ├── ceo_briefing_generator.py # CEO briefing [Gold]
│   ├── weekly_audit.py          # Weekly business audit [Gold]
│   ├── dashboard_updater.py
│   ├── linkedin_poster.py
│   └── *.ps1 (Task schedulers)
│
├── mcp-servers/                 # MCP servers
│   ├── email-mcp/
│   ├── linkedin-mcp/
│   ├── odoo-mcp/                # Odoo accounting [Gold]
│   ├── facebook-mcp/            # Facebook integration [Gold]
│   ├── instagram-mcp/           # Instagram integration [Gold]
│   └── twitter-mcp/             # Twitter integration [Gold]
│
├── AI_Employee_Vault_Gold_Tier/ # Obsidian vault
│   ├── Needs_Action/            # New messages/tasks
│   ├── Plans/                   # Generated action plans
│   ├── Pending_Approval/        # Awaiting approval
│   ├── Approved/                # Approved actions
│   ├── In_Progress/             # Currently executing
│   ├── Done/                    # Completed actions
│   ├── Logs/                    # Watcher + audit logs
│   │   ├── audit/               # Audit logs (90+ days) [Gold]
│   │   └── weekly_reports/      # Weekly reports [Gold]
│   ├── Templates/               # Document templates
│   │   ├── ceo_briefing_template.md [Gold]
│   │   └── weekly_audit_template.md [Gold]
│   └── Dashboard.md             # Status dashboard
│
├── orchestrator.py              # Main orchestrator
├── package.json                 # Node config
├── GOLD_TIER_REQUIREMENTS.md    # Gold Tier checklist
└── README.md                    # This file
```

---

## 🛠️ Setup Guide

### 1. Install Python Dependencies

```bash
pip install google-auth google-auth-oauthlib google-api-python-client playwright
playwright install chromium
```

### 2. Install Node.js Dependencies

```bash
cd mcp-servers/email-mcp && npm install
cd ../linkedin-mcp && npm install
cd ../odoo-mcp && npm install        # Gold Tier
cd ../facebook-mcp && npm install    # Gold Tier
cd ../instagram-mcp && npm install   # Gold Tier
cd ../twitter-mcp && npm install     # Gold Tier
```

### 3. Authenticate Services

```bash
# Gmail
python watchers/gmail_watcher.py auth

# WhatsApp (scan QR code when prompted)
python watchers/whatsapp_watcher.py auth

# LinkedIn (login in browser when prompted)
python watchers/linkedin_watcher.py auth

# Facebook (Gold Tier)
python watchers/facebook_watcher.py auth

# Instagram (Gold Tier)
python watchers/instagram_watcher.py auth

# Twitter (Gold Tier)
python watchers/twitter_watcher.py auth

# Odoo (Gold Tier)
python mcp-servers/odoo-mcp/auth.py
```

### 4. Start Monitoring

```bash
# Option 1: Start individual watchers
python watchers/gmail_watcher.py start
python watchers/whatsapp_watcher.py start
python watchers/linkedin_watcher.py start
python watchers/facebook_watcher.py start    # Gold Tier
python watchers/instagram_watcher.py start   # Gold Tier
python watchers/twitter_watcher.py start     # Gold Tier

# Option 2: Use orchestrator (recommended)
python orchestrator.py run
```

### 5. Configure Obsidian

1. Open `AI_Employee_Vault_Gold_Tier/` folder in Obsidian
2. Enable community plugins if needed
3. Review action files in `Needs_Action/` folder
4. Approve actions by adding `✅` to approval requests

### 6. Enable Gold Tier Features

```bash
# Start Ralph Wiggum Loop for autonomous tasks
python scripts/ralph_wiggum_loop.py "Process all pending tasks" --vault AI_Employee_Vault_Gold_Tier

# Generate weekly audit report
python scripts/audit_logger.py report --vault AI_Employee_Vault_Gold_Tier

# Generate CEO briefing
python scripts/ceo_briefing_generator.py --vault AI_Employee_Vault_Gold_Tier
```

---

## 📊 Priority Keywords

Watchers detect messages containing these keywords:

- **Urgent**: `urgent`, `asap`, `immediate`, `quick`
- **Financial**: `invoice`, `payment`, `money`, `billing`
- **Business**: `client`, `project`, `meeting`, `deadline`
- **Support**: `help`, `issue`, `problem`, `error`, `call`, `today`

Messages with these keywords get **HIGH** priority, others get **normal** priority.

---

## 🔧 Troubleshooting

### Watcher Not Detecting Messages

1. Check logs in `AI_Employee_Vault_Gold_Tier/Logs/`
2. Verify authentication: `python watchers/<name>_watcher.py status`
3. Re-authenticate if needed: `python watchers/<name>_watcher.py auth`

### Browser Session Issues

```bash
# Kill all Chrome processes
taskkill /F /IM chrome.exe

# Clear session (WhatsApp)
rmdir /s /q watchers\.whatsapp_session

# Re-authenticate
python watchers/whatsapp_watcher.py auth
```

### Action Files Not Created

1. Check if watcher is running
2. Verify `Needs_Action/` folder exists
3. Check processed messages cache: `watchers/processed_messages.json`

### Ralph Wiggum Loop Issues

1. Check state file: `AI_Employee_Vault_Gold_Tier/In_Progress/ralph_state.json`
2. Review iteration count (max: 10 by default)
3. Check for errors in audit logs

### Audit Log Queries

```bash
# Query last 7 days
python scripts/audit_logger.py query --start-date 2026-02-26

# Query by type
python scripts/audit_logger.py query --type communication

# Query by actor
python scripts/audit_logger.py query --actor AI_Employee
```

---

## 🏆 Gold Tier Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Task Completion Rate | 99%+ | - |
| Response Time (Urgent) | < 1 hour | - |
| Audit Log Retention | 90+ days | ✅ |
| Approval Rate | > 95% | - |
| Autonomous Task Success | 90%+ | - |
| Weekly Audit Generated | Every Monday | - |

---

## 📈 Upgrade Path from Silver to Gold

See [GOLD_TIER_REQUIREMENTS.md](GOLD_TIER_REQUIREMENTS.md) for detailed checklist.

### Phase 1: Foundation ✅
- [x] Ralph Wiggum Loop
- [x] Enhanced Audit Logging

### Phase 2: Accounting (In Progress)
- [ ] Odoo Installation
- [ ] Odoo MCP Server
- [ ] Bank Feed Integration

### Phase 3: Social Media Expansion
- [ ] Facebook Integration
- [ ] Instagram Integration
- [ ] Twitter Integration

### Phase 4: Business Intelligence
- [ ] CEO Briefing Generator
- [ ] Weekly Audit Automation
- [ ] Financial Reconciliation

### Phase 5: Documentation
- [ ] Architecture Documentation
- [ ] Lessons Learned
- [ ] Gold Tier README (This file) ✅

---

*Gold Tier AI Employee - Autonomous Business Partner*
*From reactive assistant to proactive CEO briefing generator*
