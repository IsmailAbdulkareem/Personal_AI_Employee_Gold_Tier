# Scripts - Silver Tier

Python scripts for AI Employee operations.

## Scripts

| Script | Purpose |
|--------|---------|
| `plan_generator.py` | Generate action plans for tasks |
| `approval_workflow.py` | Manage human-in-the-loop approvals |
| `linkedin_poster.py` | Create and post LinkedIn content |

## Usage

### Plan Generator
```bash
# Generate plans for all tasks
python scripts/plan_generator.py generate

# Generate plan for specific file
python scripts/plan_generator.py generate --file "TASK_123.md"

# Review existing plans
python scripts/plan_generator.py review
```

### Approval Workflow
```bash
# Check pending approvals
python scripts/approval_workflow.py check

# Execute approved actions
python scripts/approval_workflow.py execute

# View approval history
python scripts/approval_workflow.py history

# Create approval request
python scripts/approval_workflow.py request --type "email" --details "{}"
```

### LinkedIn Poster
```bash
# Create draft post
python scripts/linkedin_poster.py draft --topic "business update"

# Create and post
python scripts/linkedin_poster.py post --topic "project milestone"

# Publish approved posts
python scripts/linkedin_poster.py publish

# Authenticate (first time)
python scripts/linkedin_poster.py auth
```

## Requirements

Install dependencies:
```bash
pip install playwright
playwright install chromium
```
