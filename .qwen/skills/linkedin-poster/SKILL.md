# LinkedIn Poster

Automatically create and post business content to LinkedIn to generate sales and engagement.

## What this skill does

This skill enables autonomous LinkedIn marketing by:
1. Generating business-focused posts from vault content
2. Creating engaging professional content
3. Posting to LinkedIn via browser automation
4. Scheduling posts for optimal engagement times
5. Tracking post performance and engagement

## When to use this skill

Use this skill when:
- You want to maintain active LinkedIn presence
- Business updates should be shared automatically
- Lead generation through social media is needed
- Content marketing should run on autopilot

## How it works

The poster follows this pattern:
1. **Generate Content**: Create post from business goals/events
2. **Draft**: Save draft to `Pending_Approval/` folder
3. **Wait for Approval**: Human reviews and approves
4. **Post**: Use Playwright to publish on LinkedIn
5. **Log**: Record post details and engagement

## Setup Requirements

### 1. Install Playwright

```bash
pip install playwright
playwright install chromium
```

### 2. LinkedIn Authentication

```bash
python scripts/linkedin_poster.py auth
```

## Usage

```bash
# Create and post content
python scripts/linkedin_poster.py post --topic "business update"

# Generate post draft only
python scripts/linkedin_poster.py draft --topic "project milestone"

# Authenticate (first time)
python scripts/linkedin_poster.py auth

# Check status
python scripts/linkedin_poster.py status
```

## Post Types

- **Milestone**: Project achievements and business milestones
- **Insight**: Thought leadership and industry insights
- **Success**: Client success stories
- **Update**: General business updates

## Safety Features

- **Approval Required**: All posts need human approval
- **Draft First**: Never posts without review
- **Session Secure**: Credentials stored locally
- **Rate Limited**: Max 3 posts/day to avoid spam
- **Audit Log**: All posts logged for review

## Important Notes

LinkedIn automation may violate LinkedIn Terms of Service. Use responsibly:
- Don't spam or post excessive promotional content
- Maintain authentic engagement
- Follow LinkedIn Professional Community Policies

---
*Part of Silver Tier AI Employee - Social Media Automation*
