# Gold Tier AI Employee - Architecture Documentation

**Version:** 1.0  
**Last Updated:** 2026-03-04  
**Tier:** Gold

---

## System Overview

The Gold Tier AI Employee is an autonomous business partner that manages communications, accounting, and social media across multiple platforms with full audit logging and human-in-the-loop approval workflows.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         GOLD TIER AI EMPLOYEE                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                      PERCEPTION LAYER (Watchers)                  │  │
│  │  ┌────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │  │
│  │  │ Gmail  │ │ WhatsApp │ │ LinkedIn │ │ Facebook │ │Instagram │ │  │
│  │  │Watcher │ │ Watcher  │ │ Watcher  │ │ Watcher  │ │ Watcher  │ │  │
│  │  └────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘ │  │
│  │  ┌──────────┐ ┌──────────┐                                       │  │
│  │  │ Twitter  │ │ File     │                                       │  │
│  │  │ Watcher  │ │ Watcher  │                                       │  │
│  │  └──────────┘ └──────────┘                                       │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                    │                                    │
│                                    ▼                                    │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    REASONING LAYER (Orchestrator)                 │  │
│  │  ┌────────────────────────────────────────────────────────────┐  │  │
│  │  │  Gold Tier Orchestrator (orchestrator.py)                  │  │  │
│  │  │  - Task Processing                                         │  │  │
│  │  │  - Schedule Management                                     │  │  │
│  │  │  - Ralph Wiggum Loop Integration                           │  │  │
│  │  │  - Audit Logger Integration                                │  │  │
│  │  └────────────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                    │                                    │
│                    ┌───────────────┼───────────────┐                   │
│                    ▼               ▼               ▼                   │
│  ┌─────────────────────┐ ┌─────────────────┐ ┌─────────────────────┐  │
│  │   APPROVAL LAYER    │ │  MEMORY LAYER   │ │   LOGGING LAYER     │  │
│  │  ┌───────────────┐  │ │  ┌───────────┐  │ │  ┌───────────────┐  │  │
│  │  │ Pending_      │  │ │  │ Obsidian  │  │ │  │ Audit Logger  │  │  │
│  │  │ Approval/     │  │ │  │ Vault     │  │ │  │ (90+ days)    │  │  │
│  │  └───────────────┘  │ │  │ Dashboard │  │ │  └───────────────┘  │  │
│  │  ┌───────────────┐  │ │  │ Handbook  │  │ │  ┌───────────────┐  │  │
│  │  │ Approved/     │  │ │  │ Plans/    │  │ │  │ Weekly Reports│  │  │
│  │  └───────────────┘  │ │  │ Done/     │  │ │  └───────────────┘  │  │
│  └─────────────────────┘ │  └───────────┘  │ └─────────────────────┘  │
│                          └─────────────────┘                            │
│                                    │                                    │
│                                    ▼                                    │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                      ACTION LAYER (MCP Servers)                   │  │
│  │  ┌────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │  │
│  │  │ Email  │ │ LinkedIn │ │ Facebook │ │Instagram │ │ Twitter  │ │  │
│  │  │ MCP    │ │ MCP      │ │ MCP      │ │ MCP      │ │ MCP      │ │  │
│  │  └────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘ │  │
│  │  ┌──────────┐ ┌──────────┐                                       │  │
│  │  │ Odoo     │ │ Browser  │                                       │  │
│  │  │ (Accounting)│ (Playwright)│                                   │  │
│  │  └──────────┘ └──────────┘                                       │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. Perception Layer (Watchers)

**Purpose:** Monitor external platforms for new activity

**Pattern:** Passive monitoring with active file creation

**Watchers:**
| Watcher | Interval | Platform | Status |
|---------|----------|----------|--------|
| Gmail | 120s | Gmail API | ✅ Working |
| WhatsApp | 30s | WhatsApp Web | ✅ Working |
| LinkedIn | 60s | LinkedIn Web | ✅ Working |
| Facebook | 60s | Facebook Graph API | 🟡 Planned |
| Instagram | 60s | Instagram Graph API | 🟡 Planned |
| Twitter | 60s | Twitter API v2 | 🟡 Planned |
| File System | 30s | Local filesystem | ✅ Working |

**Output:** Creates `.md` files in `AI_Employee_Vault_Gold_Tier/Needs_Action/`

---

### 2. Reasoning Layer (Orchestrator)

**Purpose:** Central coordination and task management

**Key Components:**
- `orchestrator.py` - Main orchestration loop
- `ralph_wiggum_loop.py` - Autonomous task completion
- `plan_generator.py` - Action plan creation
- `approval_workflow_enhanced.py` - Approval management

**Responsibilities:**
1. Poll `Needs_Action/` folder for new tasks
2. Generate plans for complex tasks
3. Create approval requests for sensitive actions
4. Execute approved actions via MCP servers
5. Update dashboard and audit logs
6. Run scheduled tasks (daily briefing, weekly audit)

---

### 3. Approval Layer (Human-in-the-Loop)

**Purpose:** Ensure human oversight for sensitive actions

**Workflow:**
```
Needs_Action → Plans → Pending_Approval → Approved → Done
                                         ↓
                                      Rejected
```

**Always Requires Approval:**
- External communications (email, social media)
- Financial transactions (any amount)
- File deletions
- Contract changes

**Auto-Approved:**
- File reads within vault
- Dashboard updates
- Log creation
- Plan generation

---

### 4. Memory Layer (Obsidian Vault)

**Purpose:** Long-term storage and human-readable interface

**Structure:**
```
AI_Employee_Vault_Gold_Tier/
├── Needs_Action/         # New tasks to process
├── Plans/                # Generated action plans
├── Pending_Approval/     # Awaiting human approval
├── Approved/             # Approved, ready to execute
├── In_Progress/          # Currently being executed
├── Done/                 # Completed tasks
├── Logs/                 # System and audit logs
│   └── audit/            # 90+ days retention
├── Briefings/            # CEO briefings
├── Templates/            # Document templates
├── Dashboard.md          # Real-time status
└── Company_Handbook.md   # Operating rules
```

---

### 5. Logging Layer (Audit System)

**Purpose:** Comprehensive audit trail with 90+ days retention

**Implementation:** `scripts/audit_logger.py`

**Features:**
- JSONL format (one event per line)
- Automatic daily rotation
- Compression for logs > 7 days old
- Query interface for historical analysis
- Weekly report generation

**Event Types:**
- `communication` - External communications
- `approval` - Approval decisions
- `file_operation` - File reads/writes/moves
- `mcp_action` - MCP server actions
- `task_completion` - Completed tasks
- `error` - System errors
- `dashboard_update` - Dashboard refreshes
- `audit` - Audit events

---

### 6. Action Layer (MCP Servers)

**Purpose:** Execute actions on external platforms

**Pattern:** Model Context Protocol (MCP) over JSON-RPC

**MCP Servers:**
| Server | Purpose | Status |
|--------|---------|--------|
| email-mcp | Send/reply emails | ✅ Working |
| linkedin-mcp | LinkedIn posts/messages | ✅ Working |
| odoo-mcp | Accounting/invoicing | 🟡 Planned |
| facebook-mcp | Facebook posts | 🟡 Planned |
| instagram-mcp | Instagram posts | 🟡 Planned |
| twitter-mcp | Twitter posts | 🟡 Planned |

---

## Data Flow

### Standard Task Flow
```
1. Watcher detects new message
   ↓
2. Creates action file in Needs_Action/
   ↓
3. Orchestrator polls and detects file
   ↓
4. Plan Generator creates plan in Plans/
   ↓
5. Approval Workflow creates request in Pending_Approval/
   ↓
6. Human reviews and moves to Approved/
   ↓
7. Orchestrator executes via MCP server
   ↓
8. Result logged in audit system
   ↓
9. File moved to Done/
   ↓
10. Dashboard updated
```

### Ralph Wiggum Loop (Autonomous Tasks)
```
1. Orchestrator creates state file
   ↓
2. Claude processes task
   ↓
3. Claude attempts to exit
   ↓
4. Stop hook checks: Task complete?
   ↓
5. NO → Block exit, re-inject prompt
6. YES → Allow exit
   ↓
7. Log completion in audit system
```

---

## Security Architecture

### Credential Management
- All credentials stored in `config/` folder
- Never committed to git (.gitignore)
- Environment variables for sensitive data
- OAuth2 tokens with refresh capability

### Session Management
- Browser sessions stored locally
- Never synced across devices
- Automatic cleanup on logout

### Audit Trail
- All actions logged with timestamp
- Actor identification (AI/Human/System)
- Outcome tracking (success/failure)
- 90+ days retention

---

## Integration Points

### External APIs
| Platform | API | Authentication |
|----------|-----|----------------|
| Gmail | Gmail API v1 | OAuth2 |
| WhatsApp | WhatsApp Web | Browser Session |
| LinkedIn | LinkedIn Web | Browser Session |
| Facebook | Graph API v18 | OAuth2 Access Token |
| Instagram | Graph API v18 | OAuth2 Access Token |
| Twitter | API v2 | Bearer Token |
| Odoo | JSON-RPC | API Key |

### Local Integrations
| Integration | Purpose |
|-------------|---------|
| Obsidian | Knowledge base / Dashboard |
| File System | Task drop folder |
| Python | Scripting and automation |
| Node.js | MCP servers |

---

## Performance Characteristics

| Metric | Target | Current |
|--------|--------|---------|
| Watcher Response Time | < 2 minutes | 30-120s |
| Task Processing Time | < 1 minute | ~30s |
| Audit Log Write | Real-time | Real-time |
| Dashboard Update | Every 30s | Every 30s |
| Ralph Loop Iteration | < 30s | ~15s |
| Log Retention | 90+ days | 90+ days |

---

## Failure Modes & Recovery

### Watcher Failures
- **Detection:** Missing heartbeat in logs
- **Recovery:** Automatic restart via orchestrator
- **Fallback:** Manual file drop in Needs_Action/

### MCP Server Failures
- **Detection:** API error responses
- **Recovery:** Retry with exponential backoff
- **Fallback:** Queue for later execution

### Ralph Wiggum Loop Failures
- **Detection:** Max iterations reached
- **Recovery:** Log error, escalate to human
- **Fallback:** Human completes task manually

### Audit Logger Failures
- **Detection:** Write errors
- **Recovery:** Buffer in memory, retry
- **Fallback:** Log to separate file

---

## Future Enhancements

### Phase 2 (Accounting)
- [ ] Odoo installation and configuration
- [ ] Bank feed integration
- [ ] Auto-categorization rules
- [ ] Financial dashboard widgets

### Phase 3 (Social Media)
- [ ] Facebook developer account setup
- [ ] Instagram business account connection
- [ ] Twitter developer account approval
- [ ] Cross-platform posting

### Phase 4 (Business Intelligence)
- [ ] Odoo integration for revenue tracking
- [ ] Advanced bottleneck detection
- [ ] Predictive analytics
- [ ] Custom report builder

---

*Architecture Documentation - Gold Tier AI Employee*
*"From reactive assistant to autonomous business partner"*
