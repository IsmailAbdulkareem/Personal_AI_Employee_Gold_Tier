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
| **Ralph Wiggum Loop** | ✅ Complete | Autonomous multi-step task completion |
| **Enhanced Audit Logging** | ✅ Complete | 90+ days retention, weekly reports |
| **Facebook Integration** | ✅ Complete | Post messages via Graph API |
| **Instagram Integration** | ✅ Complete | Post content via Graph API |
| **LinkedIn Integration** | ✅ Complete | Post & message via browser automation |
| **Email (Gmail) Integration** | ✅ Complete | Send/receive via Gmail API |
| **WhatsApp Integration** | ✅ Complete | Send/receive via browser automation |
| **Odoo Accounting** | 🟡 Code Ready | Full MCP server - needs Odoo install |
| **Twitter (X) Integration** | 🟡 Code Ready | MCP server ready - needs dev account |
| **CEO Briefing** | ✅ Complete | Weekly business audit with metrics |
| **Financial Reconciliation** | 🟡 Code Ready | Auto-categorize transactions |

### Gold Tier Commands

| Command | Description |
|---------|-------------|
| `python scripts/ralph_wiggum_loop.py "task"` | Start autonomous task loop |
| `python scripts/audit_logger.py report` | Generate weekly audit report |
| `python scripts/ceo_briefing_generator.py` | Generate CEO briefing |
| `python scripts/weekly_audit.py` | Run weekly business audit |

---

## 👁️ Watchers Overview

All watchers follow the same pattern:
- **First Run**: Scans existing messages and marks them as "already seen"
- **Monitoring**: Checks every 30-120 seconds for NEW messages
- **Action Files**: Creates `.md` files in `AI_Employee_Vault_Gold_Tier/Needs_Action/`

### Active Watchers

| Watcher | Status | Setup Command | Send/Post Command |
|---------|--------|---------------|-------------------|
| **Gmail** | ✅ Working | `python watchers/gmail_watcher.py auth` | `python watchers/email_mcp_helper.py send_email "to" "subject" "body"` |
| **WhatsApp** | ✅ Working | `python watchers/whatsapp_watcher.py auth` | `python watchers/whatsapp_mcp_helper.py send_message "Contact" "Message"` |
| **LinkedIn** | ✅ Working | `python watchers/linkedin_watcher.py auth` | `python watchers/linkedin_mcp_helper.py create_post "Content"` |
| **Facebook** | ✅ Working | Get token from Graph API Explorer | `cd mcp-servers/facebook-mcp && node post-to-facebook.js` |
| **Instagram** | ✅ Working | Get token from Graph API Explorer | `cd mcp-servers/instagram-mcp && node post-image.js` |
| **Twitter** | 🟡 Code Ready | Needs Twitter dev account | `cd mcp-servers/twitter-mcp && node index.js` |

### How Watchers Work

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
```

**Note:** For detailed watcher documentation, see `docs/WATCHERS_CLEANUP.md`

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

### Orchestrator

| Command | Description |
|---------|-------------|
| `python orchestrator.py process` | Process all Needs_Action files |
| `python orchestrator.py run` | Run continuous monitoring |
| `python orchestrator.py status` | Check status |

### Watchers & MCP Helpers

| Platform | Authenticate | Send/Post |
|----------|-------------|-----------|
| **Gmail** | `python watchers/gmail_watcher.py auth` | `python watchers/email_mcp_helper.py send_email "to" "subject" "body"` |
| **WhatsApp** | `python watchers/whatsapp_watcher.py auth` | `python watchers/whatsapp_mcp_helper.py send_message "Contact" "Message"` |
| **LinkedIn** | `python watchers/linkedin_watcher.py auth` | `python watchers/linkedin_mcp_helper.py create_post "Content"` |
| **Facebook** | Get token from Graph API Explorer | `cd mcp-servers/facebook-mcp && node post-to-facebook.js` |
| **Instagram** | Get token from Graph API Explorer | `cd mcp-servers/instagram-mcp && node post-image.js` |

### Gold Tier Scripts

| Command | Description |
|---------|-------------|
| `python scripts/ralph_wiggum_loop.py "task"` | Autonomous task loop |
| `python scripts/audit_logger.py report` | Weekly audit report |
| `python scripts/ceo_briefing_generator.py` | CEO briefing |
| `python scripts/weekly_audit.py` | Weekly business audit |

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

## 🏆 Gold Tier Status

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| **Ralph Wiggum Loop** | Complete | ✅ Working | Done |
| **Audit Logging** | 90+ days | ✅ Working | Done |
| **Facebook Integration** | Complete | ✅ Working | Done |
| **Instagram Integration** | Complete | ✅ Working | Done |
| **LinkedIn Integration** | Complete | ✅ Working | Done |
| **Email (Gmail)** | Complete | ✅ Working | Done |
| **WhatsApp** | Complete | ✅ Working | Done |
| **Odoo Accounting** | Code Ready | 🟡 Needs Install | Ready |
| **Twitter Integration** | Code Ready | 🟡 Needs Dev Account | Ready |
| **CEO Briefing** | Complete | ✅ Working | Done |

---

## 📖 Related Documentation

| Document | Purpose |
|----------|---------|
| [`GOLD_TIER_COMPLETE.md`](GOLD_TIER_COMPLETE.md) | ✅ Implementation summary - **READ THIS FIRST** |
| [`GOLD_TIER_REQUIREMENTS.md`](GOLD_TIER_REQUIREMENTS.md) | 📋 Original requirements checklist (reference) |
| [`docs/WATCHERS_CLEANUP.md`](docs/WATCHERS_CLEANUP.md) | 🧹 Watchers folder organization |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | 🏗️ System architecture |
| [`LESSONS_LEARNED.md`](LESSONS_LEARNED.md) | 💡 Implementation insights |

---

*Gold Tier AI Employee - Production Ready*
*Last Updated: March 12, 2026*
