#!/usr/bin/env python3
"""
Enhanced Audit Logging System for Gold Tier AI Employee

Provides comprehensive logging with 90+ days retention, audit trails,
and weekly review reports.
"""
import sys
import os
import json
import logging
import gzip
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from collections import defaultdict


class AuditLogger:
    """
    Enhanced audit logging system with 90+ days retention.
    
    Features:
    - Structured JSON logging
    - Automatic log rotation
    - Compression for old logs
    - Query interface for audit trails
    - Weekly report generation
    """
    
    def __init__(self, vault_path: str, retention_days: int = 90):
        self.vault_path = Path(vault_path)
        self.logs_dir = self.vault_path / 'Logs'
        self.audit_dir = self.logs_dir / 'audit'
        self.retention_days = retention_days
        
        # Ensure directories exist
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        
        # Current log file
        self.current_log_date = datetime.now().strftime('%Y-%m-%d')
        self.current_log_file = self.audit_dir / f'audit_{self.current_log_date}.jsonl'
        
        # Setup logging
        self._setup_logging()
        
        # Log rotation check
        self._check_log_rotation()
        
        # Cleanup old logs
        self._cleanup_old_logs()
    
    def _setup_logging(self):
        """Setup Python logging for audit logger"""
        log_file = self.logs_dir / 'audit_logger.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('AuditLogger')
    
    def _check_log_rotation(self):
        """Check if log rotation is needed (new day)"""
        today = datetime.now().strftime('%Y-%m-%d')
        if today != self.current_log_date:
            self.current_log_date = today
            self.current_log_file = self.audit_dir / f'audit_{self.current_log_date}.jsonl'
            self.logger.info(f"Log rotated to {self.current_log_file}")
    
    def _cleanup_old_logs(self):
        """Remove logs older than retention period"""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        
        for log_file in self.audit_dir.glob('audit_*.jsonl*'):
            # Extract date from filename
            try:
                date_str = log_file.stem.replace('audit_', '')
                log_date = datetime.strptime(date_str, '%Y-%m-%d')
                
                if log_date < cutoff_date:
                    # Compress before deleting (optional backup)
                    compressed_file = log_file.with_suffix('.jsonl.gz')
                    if not compressed_file.exists():
                        self._compress_file(log_file, compressed_file)
                    
                    # Delete old log
                    log_file.unlink()
                    self.logger.info(f"Cleaned up old log: {log_file.name}")
            except Exception as e:
                self.logger.warning(f"Error processing log file {log_file.name}: {e}")
    
    def _compress_file(self, input_path: Path, output_path: Path):
        """Compress a file using gzip"""
        with open(input_path, 'rb') as f_in:
            with gzip.open(output_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        self.logger.info(f"Compressed {input_path.name} to {output_path.name}")
    
    def log_event(
        self,
        event_type: str,
        actor: str,
        action: str,
        details: Optional[Dict[str, Any]] = None,
        outcome: str = 'success',
        related_files: Optional[List[str]] = None
    ):
        """
        Log an audit event.
        
        Args:
            event_type: Type of event (e.g., 'email_send', 'approval', 'file_operation')
            actor: Who performed the action ('AI_Employee', 'Human_User', 'System')
            action: What action was performed
            details: Additional details about the action
            outcome: 'success', 'failure', 'pending', 'rejected'
            related_files: List of related file paths
        """
        self._check_log_rotation()
        
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'actor': actor,
            'action': action,
            'details': details or {},
            'outcome': outcome,
            'related_files': related_files or [],
            'log_date': self.current_log_date
        }
        
        # Append to current log file
        with open(self.current_log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(event, ensure_ascii=False) + '\n')
        
        self.logger.debug(f"Logged event: {event_type} - {action}")
    
    # Convenience methods for common event types
    
    def log_communication(self, channel: str, action: str, recipient: str, details: Dict = None):
        """Log external communication (email, WhatsApp, LinkedIn, etc.)"""
        self.log_event(
            event_type='communication',
            actor='AI_Employee',
            action=f'{channel}_{action}',
            details={
                'channel': channel,
                'recipient': recipient,
                **(details or {})
            },
            outcome='success',
            related_files=[]
        )
    
    def log_approval_decision(self, request_type: str, decision: str, details: Dict = None):
        """Log approval decision"""
        self.log_event(
            event_type='approval',
            actor='Human_User',
            action=f'{request_type}_{decision}',
            details={
                'request_type': request_type,
                'decision': decision,
                **(details or {})
            },
            outcome=decision.lower(),
            related_files=[]
        )
    
    def log_file_operation(self, operation: str, file_path: str, details: Dict = None):
        """Log file operation (read, write, move, delete)"""
        self.log_event(
            event_type='file_operation',
            actor='AI_Employee',
            action=operation,
            details={
                'operation': operation,
                'file_path': file_path,
                **(details or {})
            },
            outcome='success',
            related_files=[file_path]
        )
    
    def log_mcp_action(self, server: str, action: str, details: Dict = None):
        """Log MCP server action"""
        self.log_event(
            event_type='mcp_action',
            actor='AI_Employee',
            action=f'{server}:{action}',
            details={
                'mcp_server': server,
                'action': action,
                **(details or {})
            },
            outcome='success',
            related_files=[]
        )
    
    def log_dashboard_update(self, metrics: Dict = None):
        """Log dashboard update"""
        self.log_event(
            event_type='dashboard_update',
            actor='AI_Employee',
            action='dashboard_refresh',
            details=metrics or {},
            outcome='success',
            related_files=['Dashboard.md']
        )
    
    def log_error(self, error_type: str, error_message: str, context: Dict = None):
        """Log error event"""
        self.log_event(
            event_type='error',
            actor='System',
            action=error_type,
            details={
                'error_type': error_type,
                'error_message': error_message,
                **(context or {})
            },
            outcome='failure',
            related_files=[]
        )
    
    def log_task_completion(self, task_file: str, duration_seconds: float, metrics: Dict = None):
        """Log task completion"""
        self.log_event(
            event_type='task_completion',
            actor='AI_Employee',
            action='task_completed',
            details={
                'task_file': task_file,
                'duration_seconds': duration_seconds,
                'metrics': metrics or {}
            },
            outcome='success',
            related_files=[task_file]
        )
    
    def query_events(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        event_type: Optional[str] = None,
        actor: Optional[str] = None,
        outcome: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Query audit events with filters.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            event_type: Filter by event type
            actor: Filter by actor
            outcome: Filter by outcome
            
        Returns:
            List of matching events
        """
        events = []
        
        # Determine which log files to search
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=self.retention_days)).strftime('%Y-%m-%d')
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        # Iterate through date range
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        current = start
        
        while current <= end:
            date_str = current.strftime('%Y-%m-%d')
            log_file = self.audit_dir / f'audit_{date_str}.jsonl'
            compressed_file = log_file.with_suffix('.jsonl.gz')
            
            # Try uncompressed first, then compressed
            file_to_read = None
            if log_file.exists():
                file_to_read = log_file
            elif compressed_file.exists():
                # Decompress on the fly
                with gzip.open(compressed_file, 'rt', encoding='utf-8') as f:
                    for line in f:
                        try:
                            event = json.loads(line.strip())
                            if self._matches_filter(event, event_type, actor, outcome):
                                events.append(event)
                        except:
                            pass
                current += timedelta(days=1)
                continue
            
            if file_to_read:
                with open(file_to_read, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            event = json.loads(line.strip())
                            if self._matches_filter(event, event_type, actor, outcome):
                                events.append(event)
                        except:
                            pass
            
            current += timedelta(days=1)
        
        return events
    
    def _matches_filter(
        self,
        event: Dict[str, Any],
        event_type: Optional[str],
        actor: Optional[str],
        outcome: Optional[str]
    ) -> bool:
        """Check if event matches filter criteria"""
        if event_type and event.get('event_type') != event_type:
            return False
        if actor and event.get('actor') != actor:
            return False
        if outcome and event.get('outcome') != outcome:
            return False
        return True
    
    def generate_weekly_report(self, week_start: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate weekly audit report.
        
        Args:
            week_start: Start date of week (YYYY-MM-DD), defaults to last Monday
            
        Returns:
            Report dictionary with statistics and insights
        """
        # Calculate week dates
        if week_start is None:
            today = datetime.now()
            days_since_monday = today.weekday()
            week_start_date = today - timedelta(days=days_since_monday)
            week_start = week_start_date.strftime('%Y-%m-%d')
        
        week_end = (datetime.strptime(week_start, '%Y-%m-%d') + timedelta(days=6)).strftime('%Y-%m-%d')
        
        # Query events for the week
        events = self.query_events(start_date=week_start, end_date=week_end)
        
        # Calculate statistics
        stats = {
            'period': {
                'start': week_start,
                'end': week_end
            },
            'total_events': len(events),
            'by_type': defaultdict(int),
            'by_actor': defaultdict(int),
            'by_outcome': defaultdict(int),
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
            'errors': [],
            'task_completions': [],
            'daily_activity': defaultdict(int)
        }
        
        # Process events
        for event in events:
            stats['by_type'][event.get('event_type', 'unknown')] += 1
            stats['by_actor'][event.get('actor', 'unknown')] += 1
            stats['by_outcome'][event.get('outcome', 'unknown')] += 1
            
            # Extract date for daily activity
            try:
                date = event.get('timestamp', '')[:10]
                stats['daily_activity'][date] += 1
            except:
                pass
            
            # Communication breakdown
            if event.get('event_type') == 'communication':
                channel = event.get('details', {}).get('channel', 'unknown')
                stats['communications'][channel] = stats['communications'].get(channel, 0) + 1
                stats['communications']['total'] += 1
            
            # Approval breakdown
            if event.get('event_type') == 'approval':
                decision = event.get('outcome', 'unknown')
                if decision in stats['approvals']:
                    stats['approvals'][decision] += 1
            
            # Collect errors
            if event.get('event_type') == 'error':
                stats['errors'].append({
                    'timestamp': event.get('timestamp'),
                    'type': event.get('details', {}).get('error_type', 'unknown'),
                    'message': event.get('details', {}).get('error_message', '')
                })
            
            # Task completions
            if event.get('event_type') == 'task_completion':
                stats['task_completions'].append({
                    'timestamp': event.get('timestamp'),
                    'task': event.get('details', {}).get('task_file', ''),
                    'duration': event.get('details', {}).get('duration_seconds', 0)
                })
        
        # Convert defaultdicts to regular dicts
        stats['by_type'] = dict(stats['by_type'])
        stats['by_actor'] = dict(stats['by_actor'])
        stats['by_outcome'] = dict(stats['by_outcome'])
        stats['daily_activity'] = dict(stats['daily_activity'])
        
        # Calculate averages
        if stats['task_completions']:
            avg_duration = sum(t['duration'] for t in stats['task_completions']) / len(stats['task_completions'])
            stats['avg_task_duration'] = avg_duration
        else:
            stats['avg_task_duration'] = 0
        
        stats['approval_rate'] = (
            stats['approvals']['approved'] / (stats['approvals']['approved'] + stats['approvals']['rejected']) * 100
            if (stats['approvals']['approved'] + stats['approvals']['rejected']) > 0
            else 0
        )
        
        return stats
    
    def save_weekly_report(self, report: Dict[str, Any], output_path: Optional[str] = None):
        """Save weekly report to file"""
        if output_path is None:
            output_path = self.logs_dir / f'weekly_report_{report["period"]["start"]}.md'
        
        report_md = self._format_report_as_markdown(report)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_md)
        
        self.logger.info(f"Weekly report saved to {output_path}")
        return output_path
    
    def _format_report_as_markdown(self, report: Dict[str, Any]) -> str:
        """Format report as Markdown"""
        md = f"""# Weekly Audit Report

**Period**: {report['period']['start']} to {report['period']['end']}

---

## Summary Statistics

| Metric | Value |
|--------|-------|
| Total Events | {report['total_events']} |
| Avg Task Duration | {report.get('avg_task_duration', 0):.1f}s |
| Approval Rate | {report.get('approval_rate', 0):.1f}% |

---

## Events by Type

| Type | Count |
|------|-------|
"""
        for event_type, count in report['by_type'].items():
            md += f"| {event_type} | {count} |\n"
        
        md += f"""
---

## Events by Actor

| Actor | Count |
|-------|-------|
"""
        for actor, count in report['by_actor'].items():
            md += f"| {actor} | {count} |\n"
        
        md += f"""
---

## Outcomes

| Outcome | Count |
|---------|-------|
"""
        for outcome, count in report['by_outcome'].items():
            md += f"| {outcome} | {count} |\n"
        
        md += f"""
---

## Communications

| Channel | Count |
|---------|-------|
| Email | {report['communications']['email']} |
| WhatsApp | {report['communications']['whatsapp']} |
| LinkedIn | {report['communications']['linkedin']} |
| **Total** | {report['communications']['total']} |

---

## Approvals

| Decision | Count |
|----------|-------|
| Approved | {report['approvals']['approved']} |
| Rejected | {report['approvals']['rejected']} |
| Pending | {report['approvals']['pending']} |

---

## Errors ({len(report['errors'])})

"""
        for error in report['errors'][:10]:  # Show first 10 errors
            md += f"- **{error['timestamp']}**: {error['type']} - {error['message']}\n"
        
        if len(report['errors']) > 10:
            md += f"\n... and {len(report['errors']) - 10} more errors\n"
        
        md += f"""
---

## Daily Activity

| Date | Events |
|------|--------|
"""
        for date in sorted(report['daily_activity'].keys()):
            md += f"| {date} | {report['daily_activity'][date]} |\n"
        
        md += """
---

*Generated by Gold Tier Audit Logger*
"""
        return md


# Global audit logger instance
_audit_logger: Optional[AuditLogger] = None


def get_audit_logger(vault_path: str) -> AuditLogger:
    """Get or create global audit logger instance"""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger(vault_path)
    return _audit_logger


def main():
    """CLI entry point for audit logger"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Gold Tier Audit Logger')
    parser.add_argument('command', choices=['log', 'query', 'report', 'cleanup'], help='Command to execute')
    parser.add_argument('--vault', default=None, help='Path to vault')
    parser.add_argument('--type', help='Event type')
    parser.add_argument('--actor', help='Actor name')
    parser.add_argument('--start-date', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', help='End date (YYYY-MM-DD)')
    parser.add_argument('--action', help='Action description')
    parser.add_argument('--outcome', help='Outcome (success/failure/pending)')
    
    args = parser.parse_args()
    
    vault_path = args.vault or os.environ.get('VAULT_PATH', 'AI_Employee_Vault_Gold_Tier')
    logger = get_audit_logger(vault_path)
    
    if args.command == 'log':
        logger.log_event(
            event_type=args.type or 'manual',
            actor=args.actor or 'Human_User',
            action=args.action or 'manual_entry',
            outcome=args.outcome or 'success'
        )
        print("Event logged successfully")
    
    elif args.command == 'query':
        events = logger.query_events(
            start_date=args.start_date,
            end_date=args.end_date,
            event_type=args.type,
            actor=args.actor,
            outcome=args.outcome
        )
        print(f"Found {len(events)} events")
        for event in events[:10]:
            print(json.dumps(event, indent=2))
    
    elif args.command == 'report':
        report = logger.generate_weekly_report(args.start_date)
        output_path = logger.save_weekly_report(report)
        print(f"Weekly report saved to: {output_path}")
    
    elif args.command == 'cleanup':
        logger._cleanup_old_logs()
        print("Old logs cleaned up")


if __name__ == '__main__':
    main()
