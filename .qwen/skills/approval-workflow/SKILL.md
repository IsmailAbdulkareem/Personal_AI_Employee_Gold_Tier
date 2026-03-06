# Approval Workflow

Human-in-the-loop approval system for sensitive AI Employee actions requiring human oversight before execution.

## What this skill does

This skill enables safe autonomous operations by:
1. Creating approval request files for sensitive actions
2. Organizing pending approvals by category
3. Tracking approval status and expiration
4. Executing approved actions automatically
5. Logging all approval decisions

## When to use this skill

Use this skill when:
- AI needs to send external communications
- Financial transactions are involved
- Important files need modification/deletion
- Any action with external consequences
- Company Handbook requires approval

## How it works

The workflow follows this pattern:
1. **Detect**: AI identifies action requiring approval
2. **Request**: Create approval file in `Pending_Approval/`
3. **Review**: Human reviews request details
4. **Decide**: Move to `Approved/` or `Rejected/`
5. **Execute**: AI completes approved action
6. **Log**: Record decision and outcome

## Usage

```bash
# Check pending approvals
python scripts/approval_workflow.py check

# Review specific approval
python scripts/approval_workflow.py review --file "APPROVAL_123.md"

# Execute all approved actions
python scripts/approval_workflow.py execute

# View approval history
python scripts/approval_workflow.py history
```

## Approval Categories

### Always Require Approval
- Email sending (any external)
- WhatsApp replies
- LinkedIn posts
- Payment transactions
- File deletions
- Contract changes

### Auto-Approve (No Approval Needed)
- File reading
- Dashboard updates
- Log creation
- Task categorization
- Plan generation

## Approval File Format

```markdown
---
type: approval_request
action: send_email
to: client@example.com
subject: Invoice #1234
created: 2026-02-26T10:30:00Z
expires: 2026-02-27T10:30:00Z
status: pending
---

# Approval Request: Send Email

## Action Details
- **To**: client@example.com
- **Subject**: Invoice #1234

## To Approve
Move this file to `/Approved` folder

## To Reject
Move this file to `/Rejected` folder
```

## Safety Features

- **Expiration**: Approvals expire after 24 hours
- **Audit Trail**: All decisions logged with timestamp
- **Double-Check**: Amount and recipient verification
- **Rollback**: Failed executions tracked

---
*Part of Silver Tier AI Employee - Human-in-the-Loop Safety*
