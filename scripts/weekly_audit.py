#!/usr/bin/env python3
"""
Weekly Audit Automation for Gold Tier AI Employee

Runs comprehensive weekly business audit including:
- Revenue analysis
- Expense tracking
- Task completion metrics
- Communication summary
- Subscription audit
- Bottleneck identification
- CEO Briefing generation
"""
import sys
import os
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional


class WeeklyAudit:
    """Automated weekly business audit system"""
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.logs_dir = self.vault_path / 'Logs'
        self.audit_dir = self.logs_dir / 'audit'
        self.reports_dir = self.logs_dir / 'weekly_reports'
        self.done_folder = self.vault_path / 'Done'
        self.plans_folder = self.vault_path / 'Plans'
        self.briefings_folder = self.vault_path / 'Briefings'
        
        # Ensure directories exist
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Import audit logger
        try:
            from scripts.audit_logger import AuditLogger
            self.audit_logger = AuditLogger(str(vault_path))
        except Exception as e:
            print(f"Warning: Audit logger not available: {e}")
            self.audit_logger = None
    
    def _get_week_dates(self, date: Optional[datetime] = None) -> tuple[str, str]:
        """Get Monday and Sunday dates for the given week"""
        if date is None:
            date = datetime.now()
        
        days_since_monday = date.weekday()
        monday = date - timedelta(days=days_since_monday)
        sunday = monday + timedelta(days=6)
        
        return monday.strftime('%Y-%m-%d'), sunday.strftime('%Y-%m-%d')
    
    def _load_audit_events(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Load audit events for the specified date range"""
        events = []
        
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
    
    def _calculate_metrics(self, events: List[Dict]) -> Dict[str, Any]:
        """Calculate comprehensive metrics from audit events"""
        metrics = {
            'total_events': len(events),
            'by_type': {},
            'by_actor': {},
            'by_outcome': {},
            'communications': {
                'email': 0,
                'whatsapp': 0,
                'linkedin': 0,
                'total': 0
            },
            'approvals': {
                'approved': 0,
                'rejected': 0,
                'pending': 0
            },
            'task_completions': [],
            'errors': [],
            'daily_activity': {}
        }
        
        for event in events:
            # Count by type
            event_type = event.get('event_type', 'unknown')
            metrics['by_type'][event_type] = metrics['by_type'].get(event_type, 0) + 1
            
            # Count by actor
            actor = event.get('actor', 'unknown')
            metrics['by_actor'][actor] = metrics['by_actor'].get(actor, 0) + 1
            
            # Count by outcome
            outcome = event.get('outcome', 'unknown')
            metrics['by_outcome'][outcome] = metrics['by_outcome'].get(outcome, 0) + 1
            
            # Track daily activity
            date = event.get('timestamp', '')[:10]
            metrics['daily_activity'][date] = metrics['daily_activity'].get(date, 0) + 1
            
            # Communication breakdown
            if event_type == 'communication':
                channel = event.get('details', {}).get('channel', 'unknown')
                if channel in metrics['communications']:
                    metrics['communications'][channel] += 1
                    metrics['communications']['total'] += 1
            
            # Approval breakdown
            if event_type == 'approval':
                if outcome in metrics['approvals']:
                    metrics['approvals'][outcome] += 1
            
            # Task completions
            if event_type == 'task_completion':
                metrics['task_completions'].append({
                    'timestamp': event.get('timestamp'),
                    'task': event.get('details', {}).get('task_file', ''),
                    'duration': event.get('details', {}).get('duration_seconds', 0)
                })
            
            # Errors
            if event_type == 'error':
                metrics['errors'].append({
                    'timestamp': event.get('timestamp'),
                    'type': event.get('details', {}).get('error_type', 'unknown'),
                    'message': event.get('details', {}).get('error_message', '')
                })
        
        # Calculate averages
        if metrics['task_completions']:
            avg_duration = sum(t['duration'] for t in metrics['task_completions']) / len(metrics['task_completions'])
            metrics['avg_task_duration'] = avg_duration
        else:
            metrics['avg_task_duration'] = 0
        
        # Calculate approval rate
        total_approvals = metrics['approvals']['approved'] + metrics['approvals']['rejected']
        metrics['approval_rate'] = (
            metrics['approvals']['approved'] / total_approvals * 100
            if total_approvals > 0
            else 0
        )
        
        return metrics
    
    def _generate_summary(self, metrics: Dict, week_start: str, week_end: str) -> str:
        """Generate audit summary markdown"""
        summary = f"""# Weekly Business Audit Report

---
generated: {datetime.now().isoformat()}
period: {week_start} to {week_end}
tier: Gold
---

## Executive Summary

This automated weekly audit provides a comprehensive overview of business operations,
communication patterns, task completion, and system performance.

---

## Activity Overview

| Metric | Value |
|--------|-------|
| **Total Events** | {metrics['total_events']} |
| **Active Days** | {len(metrics['daily_activity'])} |
| **Avg Task Duration** | {metrics['avg_task_duration']:.1f} seconds |
| **Approval Rate** | {metrics['approval_rate']:.1f}% |

---

## Events by Type

| Type | Count | Percentage |
|------|-------|------------|
"""
        
        total = metrics['total_events'] or 1
        for event_type, count in sorted(metrics['by_type'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total) * 100
            summary += f"| {event_type} | {count} | {percentage:.1f}% |\n"
        
        summary += f"""
---

## Events by Actor

| Actor | Count | Percentage |
|-------|-------|------------|
"""
        
        for actor, count in sorted(metrics['by_actor'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total) * 100
            summary += f"| {actor} | {count} | {percentage:.1f}% |\n"
        
        summary += f"""
---

## Outcomes

| Outcome | Count | Percentage |
|---------|-------|------------|
"""
        
        for outcome, count in sorted(metrics['by_outcome'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total) * 100
            summary += f"| {outcome} | {count} | {percentage:.1f}% |\n"
        
        summary += f"""
---

## Communications Summary

| Channel | Count |
|---------|-------|
| Email | {metrics['communications']['email']} |
| WhatsApp | {metrics['communications']['whatsapp']} |
| LinkedIn | {metrics['communications']['linkedin']} |
| **Total** | {metrics['communications']['total']} |

---

## Approvals

| Decision | Count |
|----------|-------|
| Approved | {metrics['approvals']['approved']} |
| Rejected | {metrics['approvals']['rejected']} |
| Pending | {metrics['approvals']['pending']} |

**Approval Rate**: {metrics['approval_rate']:.1f}%

---

## Daily Activity

| Date | Events |
|------|--------|
"""
        
        for date in sorted(metrics['daily_activity'].keys()):
            summary += f"| {date} | {metrics['daily_activity'][date]} |\n"
        
        summary += f"""
---

## Task Completions ({len(metrics['task_completions'])})

"""
        
        if metrics['task_completions']:
            summary += "| Task | Duration | Timestamp |\n"
            summary += "|------|----------|-----------|\n"
            for task in metrics['task_completions'][:10]:
                task_name = task['task'][:40]
                duration = f"{task['duration']:.1f}s"
                timestamp = task['timestamp'][:16] if task['timestamp'] else 'N/A'
                summary += f"| {task_name}... | {duration} | {timestamp} |\n"
            
            if len(metrics['task_completions']) > 10:
                summary += f"\n*... and {len(metrics['task_completions']) - 10} more tasks*\n"
        else:
            summary += "*No task completions recorded this week*\n"
        
        summary += f"""
---

## Errors ({len(metrics['errors'])})

"""
        
        if metrics['errors']:
            for error in metrics['errors'][:10]:
                summary += f"- **{error['timestamp']}**: {error['type']}\n"
                summary += f"  - {error['message']}\n"
            
            if len(metrics['errors']) > 10:
                summary += f"\n*... and {len(metrics['errors']) - 10} more errors*\n"
        else:
            summary += "*No errors recorded this week* ✅\n"
        
        summary += f"""
---

## Insights & Recommendations

### Performance Analysis
"""
        
        # Performance insights
        if metrics['avg_task_duration'] > 300:
            summary += "- ⚠️ Average task duration is high (> 5 minutes). Consider optimization.\n"
        else:
            summary += "- ✅ Task completion times are within acceptable range.\n"
        
        if metrics['approval_rate'] < 80:
            summary += "- ⚠️ Approval rate is below 80%. Review approval criteria.\n"
        else:
            summary += "- ✅ Approval rate is healthy.\n"
        
        if metrics['errors']:
            summary += f"- ⚠️ {len(metrics['errors'])} errors detected. Review error logs.\n"
        else:
            summary += "- ✅ No errors detected.\n"
        
        summary += f"""
### Communication Patterns
"""
        
        if metrics['communications']['total'] > 0:
            most_used = max(metrics['communications'].items(), key=lambda x: x[1] if x[0] != 'total' else 0)
            summary += f"- Most used channel: **{most_used[0]}** ({most_used[1]} communications)\n"
        else:
            summary += "- No communications recorded this week.\n"
        
        summary += f"""
### Action Items
"""
        
        action_items = []
        if metrics['errors']:
            action_items.append("1. Review and address recorded errors")
        if metrics['approval_rate'] < 80:
            action_items.append("2. Review approval workflow efficiency")
        if metrics['avg_task_duration'] > 300:
            action_items.append("3. Optimize slow-performing tasks")
        
        if action_items:
            summary += '\n'.join(action_items)
        else:
            summary += "*No critical action items - System operating optimally* ✅"
        
        summary += f"""

---

## Next Steps

1. **Review CEO Briefing**: Check `/Briefings/` for executive summary
2. **Address Errors**: Review error logs in `/Logs/audit/`
3. **Plan Next Week**: Use insights for upcoming priorities
4. **Archive Old Logs**: Logs older than 90 days will be auto-compressed

---

*Weekly Audit generated by Gold Tier AI Employee*
*Audit Logger: 90+ days retention*
*Next audit: {(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')}*
"""
        
        return summary
    
    def run_audit(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """Run complete weekly audit"""
        if date is None:
            date = datetime.now()
        
        week_start, week_end = self._get_week_dates(date)
        
        print(f"Running Weekly Audit...")
        print(f"Period: {week_start} to {week_end}")
        print()
        
        # Load events
        print("Loading audit events...")
        events = self._load_audit_events(week_start, week_end)
        print(f"Found {len(events)} events")
        
        # Calculate metrics
        print("Calculating metrics...")
        metrics = self._calculate_metrics(events)
        
        # Generate summary
        print("Generating audit summary...")
        summary = self._generate_summary(metrics, week_start, week_end)
        
        # Save report
        report_path = self.reports_dir / f'weekly_audit_{week_start}.md'
        report_path.write_text(summary, encoding='utf-8')
        print(f"\nAudit report saved to: {report_path}")
        
        # Log audit completion
        if self.audit_logger:
            self.audit_logger.log_event(
                event_type='audit',
                actor='AI_Employee',
                action='weekly_audit_completed',
                details={
                    'week_start': week_start,
                    'week_end': week_end,
                    'total_events': metrics['total_events'],
                    'report_path': str(report_path)
                },
                outcome='success'
            )
        
        # Generate CEO Briefing
        print("\nGenerating CEO Briefing...")
        try:
            from scripts.ceo_briefing_generator import CEOBriefingGenerator
            briefing_gen = CEOBriefingGenerator(str(self.vault_path))
            briefing = briefing_gen.generate_briefing(date)
            briefing_path = briefing_gen.save_briefing(briefing)
            print(f"CEO Briefing saved to: {briefing_path}")
        except Exception as e:
            print(f"Warning: Could not generate CEO Briefing: {e}")
        
        return {
            'week_start': week_start,
            'week_end': week_end,
            'metrics': metrics,
            'report_path': str(report_path)
        }


def main():
    """CLI entry point for Weekly Audit"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Weekly Audit Automation')
    parser.add_argument('--vault', default='AI_Employee_Vault_Gold_Tier', help='Path to vault')
    parser.add_argument('--date', default=None, help='Date for audit (YYYY-MM-DD)')
    parser.add_argument('--print', action='store_true', help='Print report to stdout')
    
    args = parser.parse_args()
    
    vault_path = Path(args.vault)
    audit = WeeklyAudit(str(vault_path))
    
    # Parse date if provided
    date = None
    if args.date:
        date = datetime.strptime(args.date, '%Y-%m-%d')
    
    # Run audit
    result = audit.run_audit(date)
    
    print("\n" + "="*60)
    print("WEEKLY AUDIT COMPLETE")
    print("="*60)
    print(f"Period: {result['week_start']} to {result['week_end']}")
    print(f"Total Events: {result['metrics']['total_events']}")
    print(f"Report: {result['report_path']}")
    print("="*60)


if __name__ == '__main__':
    main()
