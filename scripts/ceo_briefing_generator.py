#!/usr/bin/env python3
"""
CEO Briefing Generator for Gold Tier AI Employee

Generates comprehensive Monday Morning CEO Briefings with:
- Revenue metrics
- Bottleneck analysis
- Completed tasks summary
- Proactive suggestions
- Subscription audit
- Upcoming deadlines
"""
import sys
import os
import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional


class CEOBriefingGenerator:
    """Generate weekly CEO briefings for business insights"""
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.logs_dir = self.vault_path / 'Logs'
        self.audit_dir = self.logs_dir / 'audit'
        self.done_folder = self.vault_path / 'Done'
        self.plans_folder = self.vault_path / 'Plans'
        self.briefings_folder = self.vault_path / 'Briefings'
        self.handbook_path = self.vault_path / 'Company_Handbook.md'
        self.dashboard_path = self.vault_path / 'Dashboard.md'
        
        # Ensure briefings folder exists
        self.briefings_folder.mkdir(parents=True, exist_ok=True)
        
        # Subscription patterns for audit
        self.subscription_patterns = {
            'netflix.com': 'Netflix',
            'spotify.com': 'Spotify',
            'adobe.com': 'Adobe Creative Cloud',
            'notion.so': 'Notion',
            'slack.com': 'Slack',
            'zoom.us': 'Zoom',
            'microsoft.com': 'Microsoft 365',
            'github.com': 'GitHub',
            'aws.amazon.com': 'Amazon Web Services',
            'cloud.google.com': 'Google Cloud',
        }
    
    def _get_week_dates(self, date: Optional[datetime] = None) -> tuple[str, str]:
        """Get Monday and Sunday dates for the given week"""
        if date is None:
            date = datetime.now()
        
        # Find last Monday (or today if it's Monday)
        days_since_monday = date.weekday()
        monday = date - timedelta(days=days_since_monday)
        sunday = monday + timedelta(days=6)
        
        return monday.strftime('%Y-%m-%d'), sunday.strftime('%Y-%m-%d')
    
    def _load_audit_events(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Load audit events for the specified date range"""
        events = []
        
        # Parse dates
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        current = start
        
        while current <= end:
            date_str = current.strftime('%Y-%m-%d')
            log_file = self.audit_dir / f'audit_{date_str}.jsonl'
            
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            event = json.loads(line.strip())
                            events.append(event)
                        except:
                            pass
            
            current += timedelta(days=1)
        
        return events
    
    def _analyze_revenue(self, events: List[Dict]) -> Dict[str, Any]:
        """Analyze revenue from audit events"""
        revenue_data = {
            'total': 0,
            'transactions': [],
            'by_type': {},
            'pending': 0,
            'received': 0
        }
        
        for event in events:
            if event.get('event_type') == 'payment':
                details = event.get('details', {})
                amount = details.get('amount', 0)
                
                if isinstance(amount, (int, float)):
                    revenue_data['total'] += amount
                    revenue_data['transactions'].append({
                        'date': event.get('timestamp', '')[:10],
                        'amount': amount,
                        'type': details.get('type', 'unknown'),
                        'status': event.get('outcome', 'unknown')
                    })
                    
                    # Categorize by type
                    tx_type = details.get('type', 'other')
                    revenue_data['by_type'][tx_type] = revenue_data['by_type'].get(tx_type, 0) + amount
                    
                    # Track by outcome
                    if event.get('outcome') == 'success':
                        revenue_data['received'] += amount
                    else:
                        revenue_data['pending'] += amount
        
        return revenue_data
    
    def _analyze_bottlenecks(self, events: List[Dict]) -> List[Dict[str, Any]]:
        """Identify bottlenecks from task completion data"""
        bottlenecks = []
        task_durations = []
        
        for event in events:
            if event.get('event_type') == 'task_completion':
                details = event.get('details', {})
                duration = details.get('duration_seconds', 0)
                task_file = details.get('task_file', '')
                
                if duration > 0:
                    task_durations.append({
                        'task': task_file,
                        'duration': duration,
                        'timestamp': event.get('timestamp', '')
                    })
        
        # Identify slow tasks (> 5 minutes or 300 seconds)
        avg_duration = sum(t['duration'] for t in task_durations) / len(task_durations) if task_durations else 0
        
        for task in task_durations:
            if task['duration'] > max(300, avg_duration * 2):
                bottlenecks.append({
                    'task': task['task'],
                    'duration': task['duration'],
                    'expected': min(300, avg_duration),
                    'delay': task['duration'] - avg_duration
                })
        
        return bottlenecks
    
    def _analyze_subscriptions(self, events: List[Dict]) -> List[Dict[str, Any]]:
        """Analyze subscription costs and usage"""
        subscriptions = {}
        
        for event in events:
            details = event.get('details', {})
            description = details.get('description', '').lower()
            amount = details.get('amount', 0)
            
            # Check against known patterns
            for pattern, name in self.subscription_patterns.items():
                if pattern in description:
                    if name not in subscriptions:
                        subscriptions[name] = {
                            'name': name,
                            'pattern': pattern,
                            'total_cost': 0,
                            'transactions': [],
                            'last_payment': None
                        }
                    
                    subscriptions[name]['total_cost'] += amount
                    subscriptions[name]['transactions'].append({
                        'date': event.get('timestamp', '')[:10],
                        'amount': amount
                    })
                    subscriptions[name]['last_payment'] = event.get('timestamp', '')[:10]
        
        # Generate recommendations
        recommendations = []
        for name, data in subscriptions.items():
            # Flag expensive or unused subscriptions
            if data['total_cost'] > 50:
                recommendations.append({
                    'subscription': name,
                    'issue': 'high_cost',
                    'message': f"Cost: ${data['total_cost']:.2f} this week - Review for optimization",
                    'action': 'Review usage and consider downgrade'
                })
        
        return list(subscriptions.values()), recommendations
    
    def _get_completed_tasks(self, date: str) -> List[str]:
        """Get list of tasks completed today"""
        tasks = []
        
        if self.done_folder.exists():
            for task_file in self.done_folder.glob('*.md'):
                # Check if file was modified today
                mtime = datetime.fromtimestamp(task_file.stat().st_mtime)
                if mtime.strftime('%Y-%m-%d') == date:
                    tasks.append(task_file.stem)
        
        return tasks
    
    def _get_upcoming_deadlines(self) -> List[Dict[str, str]]:
        """Extract upcoming deadlines from plans"""
        deadlines = []
        
        if self.plans_folder.exists():
            for plan_file in self.plans_folder.glob('*.md'):
                content = plan_file.read_text(encoding='utf-8')
                
                # Look for deadline patterns
                deadline_match = re.search(r'deadline:\s*(\d{4}-\d{2}-\d{2})', content, re.IGNORECASE)
                if deadline_match:
                    deadline = deadline_match.group(1)
                    # Only include future deadlines
                    if deadline >= datetime.now().strftime('%Y-%m-%d'):
                        deadlines.append({
                            'task': plan_file.stem,
                            'deadline': deadline
                        })
        
        # Sort by deadline
        deadlines.sort(key=lambda x: x['deadline'])
        
        return deadlines[:10]  # Return top 10
    
    def _load_business_goals(self) -> Dict[str, Any]:
        """Load business goals from handbook or goals file"""
        goals_file = self.vault_path / 'Business_Goals.md'
        
        if goals_file.exists():
            content = goals_file.read_text(encoding='utf-8')
            # Simple parsing - extract key metrics
            goals = {
                'raw': content,
                'monthly_revenue_target': 10000,  # Default
                'active_projects': []
            }
            
            # Try to extract revenue target
            match = re.search(r'Monthly goal:?\s*\$?(\d+)', content)
            if match:
                goals['monthly_revenue_target'] = int(match.group(1))
            
            return goals
        
        return {
            'monthly_revenue_target': 10000,
            'active_projects': []
        }
    
    def generate_briefing(self, date: Optional[datetime] = None) -> str:
        """Generate complete CEO briefing"""
        if date is None:
            date = datetime.now()
        
        # Get week dates
        week_start, week_end = self._get_week_dates(date)
        
        # Load audit events
        events = self._load_audit_events(week_start, week_end)
        
        # Analyze data
        revenue = self._analyze_revenue(events)
        bottlenecks = self._analyze_bottlenecks(events)
        subscriptions, subscription_recommendations = self._analyze_subscriptions(events)
        completed_tasks = self._get_completed_tasks(date.strftime('%Y-%m-%d'))
        deadlines = self._get_upcoming_deadlines()
        goals = self._load_business_goals()
        
        # Calculate metrics
        days_into_month = date.day
        monthly_target = goals.get('monthly_revenue_target', 10000)
        expected_progress = (days_into_month / 30) * 100
        actual_progress = (revenue['total'] / monthly_target * 100) if monthly_target > 0 else 0
        
        # Generate briefing
        briefing = f"""# Monday Morning CEO Briefing

---
generated: {datetime.now().isoformat()}
period: {week_start} to {week_end}
tier: Gold
---

## Executive Summary

**Overall Status**: {'🟢 On Track' if actual_progress >= expected_progress else '🟡 Behind Target'}

This week's performance analysis with revenue tracking, bottleneck identification, and proactive recommendations.

---

## Revenue Analysis

### Weekly Revenue

| Metric | Amount | Status |
|--------|--------|--------|
| **Total Revenue** | ${revenue['total']:.2f} | {'✅' if revenue['total'] > 0 else '⚠️'} |
| **Received** | ${revenue['received']:.2f} | - |
| **Pending** | ${revenue['pending']:.2f} | {'⚠️' if revenue['pending'] > 0 else '✅'} |

### Monthly Progress

| Metric | Value |
|--------|-------|
| Monthly Target | ${monthly_target:,.2f} |
| Current Revenue | ${revenue['total']:,.2f} |
| Expected Progress | {expected_progress:.1f}% |
| Actual Progress | {actual_progress:.1f}% |
| Status | {'✅ On Track' if actual_progress >= expected_progress else '🟡 Behind'} |

### Revenue by Type

"""
        
        if revenue['by_type']:
            for tx_type, amount in revenue['by_type'].items():
                briefing += f"- **{tx_type}**: ${amount:.2f}\n"
        else:
            briefing += "*No revenue transactions recorded this week*\n"
        
        briefing += f"""
---

## Completed Tasks

"""
        
        if completed_tasks:
            for task in completed_tasks[:10]:
                briefing += f"- [x] {task}\n"
            if len(completed_tasks) > 10:
                briefing += f"- ... and {len(completed_tasks) - 10} more\n"
        else:
            briefing += "*No tasks completed today*\n"
        
        briefing += f"""
---

## Bottlenecks Identified

"""
        
        if bottlenecks:
            briefing += "| Task | Actual | Expected | Delay |\n"
            briefing += "|------|--------|----------|-------|\n"
            for bottleneck in bottlenecks[:5]:
                briefing += f"| {bottleneck['task'][:30]}... | {bottleneck['duration']:.0f}s | {bottleneck['expected']:.0f}s | +{bottleneck['delay']:.0f}s |\n"
        else:
            briefing += "*No significant bottlenecks detected* ✅\n"
        
        briefing += f"""
---

## Subscription Audit

"""
        
        if subscriptions:
            briefing += "| Subscription | Total Cost | Last Payment |\n"
            briefing += "|--------------|------------|---------------|\n"
            for sub in subscriptions:
                briefing += f"| {sub['name']} | ${sub['total_cost']:.2f} | {sub['last_payment']} |\n"
            
            if subscription_recommendations:
                briefing += "\n### Recommendations\n\n"
                for rec in subscription_recommendations:
                    briefing += f"- ⚠️ **{rec['subscription']}**: {rec['message']}\n"
                    briefing += f"  - Action: {rec['action']}\n"
        else:
            briefing += "*No subscription payments detected this week*\n"
        
        briefing += f"""
---

## Upcoming Deadlines

"""
        
        if deadlines:
            briefing += "| Task | Deadline | Days Remaining |\n"
            briefing += "|------|----------|----------------|\n"
            for deadline in deadlines:
                days_remaining = (datetime.strptime(deadline['deadline'], '%Y-%m-%d') - datetime.now()).days
                briefing += f"| {deadline['task'][:30]}... | {deadline['deadline']} | {days_remaining} |\n"
        else:
            briefing += "*No upcoming deadlines found*\n"
        
        briefing += f"""
---

## Proactive Suggestions

### Cost Optimization
"""
        
        if subscription_recommendations:
            for rec in subscription_recommendations[:3]:
                briefing += f"- {rec['message']}\n"
        else:
            briefing += "- No cost optimization opportunities identified\n"
        
        briefing += """
### Revenue Opportunities
"""
        
        if revenue['pending'] > 0:
            briefing += f"- Follow up on ${revenue['pending']:.2f} in pending payments\n"
        if actual_progress < expected_progress:
            briefing += f"- Revenue is {expected_progress - actual_progress:.1f}% behind expected progress - Consider outreach\n"
        if not deadlines:
            briefing += "- Capacity available for new projects\n"
        
        briefing += f"""
### Operational Efficiency
"""
        
        if bottlenecks:
            briefing += f"- Review {len(bottlenecks)} bottleneck(s) identified above\n"
        else:
            briefing += "- Operations running efficiently\n"
        
        briefing += f"""
---

## Key Metrics Summary

| Metric | Value | Trend |
|--------|-------|-------|
| Revenue This Week | ${revenue['total']:,.2f} | {'📈' if revenue['total'] > 0 else '➡️'} |
| Tasks Completed Today | {len(completed_tasks)} | ➡️ |
| Bottlenecks | {len(bottlenecks)} | {'📉' if len(bottlenecks) == 0 else '⚠️'} |
| Pending Payments | ${revenue['pending']:,.2f} | {'⚠️' if revenue['pending'] > 0 else '✅'} |
| Monthly Progress | {actual_progress:.1f}% | {'📈' if actual_progress >= expected_progress else '📉'} |

---

## Action Items for CEO

"""
        
        action_items = []
        
        if revenue['pending'] > 0:
            action_items.append(f"1. Review ${revenue['pending']:.2f} in pending payments")
        
        if subscription_recommendations:
            action_items.append(f"2. Review {len(subscription_recommendations)} subscription recommendation(s)")
        
        if bottlenecks:
            action_items.append(f"3. Address {len(bottlenecks)} bottleneck(s)")
        
        if actual_progress < expected_progress:
            action_items.append("4. Consider revenue generation activities")
        
        if action_items:
            briefing += '\n'.join(action_items)
        else:
            briefing += "*No critical action items - All systems operational* ✅"
        
        briefing += f"""

---

*Briefing generated by Gold Tier AI Employee*
*Next briefing: {(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')}*
"""
        
        return briefing
    
    def save_briefing(self, briefing: str, output_path: Optional[str] = None) -> Path:
        """Save briefing to file"""
        if output_path is None:
            date_str = datetime.now().strftime('%Y-%m-%d')
            output_path = self.briefings_folder / f'{date_str}_CEO_Briefing.md'
        
        output_path = Path(output_path)
        output_path.write_text(briefing, encoding='utf-8')
        
        print(f"CEO Briefing saved to: {output_path}")
        return output_path


def main():
    """CLI entry point for CEO Briefing Generator"""
    import argparse
    
    parser = argparse.ArgumentParser(description='CEO Briefing Generator')
    parser.add_argument('--vault', default='AI_Employee_Vault_Gold_Tier', help='Path to vault')
    parser.add_argument('--output', default=None, help='Output file path')
    parser.add_argument('--date', default=None, help='Date for briefing (YYYY-MM-DD)')
    parser.add_argument('--print', action='store_true', help='Print to stdout instead of saving')
    
    args = parser.parse_args()
    
    vault_path = Path(args.vault)
    generator = CEOBriefingGenerator(str(vault_path))
    
    # Parse date if provided
    date = None
    if args.date:
        date = datetime.strptime(args.date, '%Y-%m-%d')
    
    # Generate briefing
    print("Generating CEO Briefing...")
    briefing = generator.generate_briefing(date)
    
    if args.print:
        print(briefing)
    else:
        output_path = generator.save_briefing(briefing, args.output)
        print(f"\nBriefing saved successfully!")
        print(f"Location: {output_path}")


if __name__ == '__main__':
    main()
