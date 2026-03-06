# Plan Generator

Automatically create detailed action plans (Plan.md files) for tasks in the AI Employee vault using Claude's reasoning capabilities.

## What this skill does

This skill enables autonomous planning by:
1. Analyzing tasks in `Needs_Action/` folder
2. Breaking down complex tasks into actionable steps
3. Creating structured Plan.md files with checkboxes
4. Estimating effort and priority
5. Linking related tasks and dependencies

## When to use this skill

Use this skill when:
- Complex tasks need structured breakdown
- Multiple steps must be tracked
- Task dependencies exist
- You want visibility into execution strategy

## How it works

The generator follows this pattern:
1. **Read**: Analyze task files in `Needs_Action/`
2. **Think**: Understand requirements and constraints
3. **Plan**: Create structured plan with steps
4. **Write**: Save Plan.md to `Plans/` folder

## Usage

```bash
# Generate plans for all pending tasks
python scripts/plan_generator.py generate

# Generate plan for specific file
python scripts/plan_generator.py generate --file "TASK_123.md"

# Review existing plans
python scripts/plan_generator.py review
```

## Plan Types

- **Email Response Plan** (15 min estimate)
- **Invoice Request Plan** (30 min estimate)
- **Client Onboarding Plan** (2 hours estimate)
- **Document Processing Plan** (45 min estimate)
- **Generic Task Plan** (30 min estimate)

## Plan File Format

```markdown
---
type: action_plan
task_id: TASK_20260226_client_invoice
created: 2026-02-26T10:30:00Z
status: pending
priority: high
estimated_effort: 30 minutes
---

# Action Plan: Client Invoice Request

## Objective
Generate and send invoice to client for January services.

## Steps
- [ ] Review client contract for rates
- [ ] Calculate total hours worked
- [ ] Generate invoice PDF
- [ ] Create approval request
- [ ] Send invoice after approval
- [ ] Log transaction

## Success Criteria
- Invoice sent within 24 hours
- Payment tracked in accounting
```

---
*Part of Silver Tier AI Employee - Reasoning Loop*
