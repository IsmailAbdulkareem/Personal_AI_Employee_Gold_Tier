#!/usr/bin/env python3
"""
Approval Workflow Skill for AI Employee - ENHANCED
Human-in-the-loop approval system with real action execution
"""
import sys
import os
import json
import shutil
import argparse
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class ApprovalWorkflow:
    """Manage human-in-the-loop approval workflow"""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.pending = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.rejected = self.vault_path / 'Rejected'
        self.done = self.vault_path / 'Done'
        self.logs = self.vault_path / 'Logs'

        for folder in [self.pending, self.approved, self.rejected, self.done, self.logs]:
            folder.mkdir(parents=True, exist_ok=True)

        self.approval_log = self.logs / 'approvals.jsonl'
        self.expiration_hours = 24
        self.logger = logging.getLogger('ApprovalWorkflow')
        self.watchers_dir = Path(__file__).parent.parent / 'watchers'

    def create_approval_request(self, request_type: str, details: dict,
                                 content: str = "", priority: str = "medium") -> Path:
        """Create a new approval request file"""
        timestamp = datetime.now()
        expires = timestamp + timedelta(hours=self.expiration_hours)

        safe_type = request_type.upper().replace(' ', '_')[:20]
        filename = f"{safe_type}_APPROVAL_{timestamp.strftime('%Y%m%d_%H%M%S')}.md"

        details_text = '\n'.join([f"- **{k.replace('_', ' ').title()}**: {v}" for k, v in details.items()]) if details else "*No additional details*"

        md_content = f"""---
type: approval_request
action: {request_type}
created: {timestamp.isoformat()}
expires: {expires.isoformat()}
status: pending
priority: {priority}
---

# Approval Request: {request_type.replace('_', ' ').title()}

## Action Details
{details_text}

## Context
{content if content else 'Action requires human approval per Company Handbook.'}

## Instructions

### To Approve
Move this file to `/Approved` folder

### To Reject
Move this file to `/Rejected` folder with reason

---
*Expires: {expires.strftime('%Y-%m-%d %H:%M')} if not actioned*
"""

        filepath = self.pending / filename
        filepath.write_text(md_content, encoding='utf-8')

        self._log_approval(filename, 'created', request_type, details)

        return filepath

    def check_pending(self) -> list:
        """Check all pending approval requests"""
        if not self.pending.exists():
            return []

        pending_requests = []
        now = datetime.now()

        for f in self.pending.glob('*.md'):
            content = f.read_text(encoding='utf-8')

            request_info = {
                'file': f.name,
                'path': str(f),
                'type': 'unknown',
                'priority': 'medium',
                'expires': None,
                'expired': False
            }

            for line in content.split('\n')[:15]:
                if 'action:' in line:
                    request_info['type'] = line.split(':')[1].strip()
                if 'priority:' in line:
                    request_info['priority'] = line.split(':')[1].strip()
                if 'expires:' in line:
                    request_info['expires'] = line.split(':')[1].strip()

            if request_info['expires']:
                try:
                    expires = datetime.fromisoformat(request_info['expires'])
                    request_info['expired'] = now > expires
                except:
                    pass

            pending_requests.append(request_info)

        return pending_requests

    def check_approved(self) -> list:
        """Check all approved actions ready for execution"""
        if not self.approved.exists():
            return []

        approved_actions = []
        for f in self.approved.glob('*.md'):
            content = f.read_text(encoding='utf-8')
            if 'type: approval_request' in content:
                approved_actions.append({
                    'file': f.name,
                    'path': str(f),
                    'content': content
                })

        return approved_actions

    def execute_approved_actions(self) -> list:
        """Execute all approved actions in Approved/ folder"""
        if not self.approved.exists():
            return []

        results = []
        executed_count = 0

        for action_file in sorted(self.approved.glob('*.md')):
            try:
                action = {
                    'path': str(action_file),
                    'file': action_file.name,
                    'content': action_file.read_text(encoding='utf-8')
                }

                # Parse action type from frontmatter
                action_type = 'unknown'
                details = {}
                for line in action['content'].split('\n')[:25]:
                    line_lower = line.lower()
                    if 'action:' in line_lower:
                        action_type = line.split(':', 1)[1].strip().lower()
                    if 'to:' in line_lower and '@' in line:
                        details['to'] = line.split(':', 1)[1].strip()
                    if 'subject:' in line_lower:
                        details['subject'] = line.split(':', 1)[1].strip()
                    if 'recipient:' in line_lower:
                        details['recipient'] = line.split(':', 1)[1].strip()
                    if 'message:' in line_lower:
                        details['message'] = line.split(':', 1)[1].strip()

                self.logger.info(f"Executing {action_type}: {action['file']}")

                # Execute based on action type
                result = self._execute_action(action_type, action, details)
                result['file'] = action['file']
                result['action_type'] = action_type
                results.append(result)

                if result['success']:
                    dest = self.done / action['file']
                    shutil.move(str(action_file), str(dest))
                    self._log_approval(action['file'], 'executed', action_type, details)
                    executed_count += 1
                    self.logger.info(f"✓ Successfully executed: {action['file']}")
                else:
                    self.logger.error(f"✗ Failed to execute {action['file']}: {result.get('error', 'Unknown')}")

            except Exception as e:
                results.append({
                    'file': action_file.name,
                    'success': False,
                    'error': str(e)
                })
                self.logger.error(f"Exception executing {action_file.name}: {e}")

        self.logger.info(f"Executed {executed_count}/{len(results)} approved actions")
        return results

    def _execute_action(self, action_type: str, action: dict, details: dict) -> dict:
        """Execute a specific action type"""
        action_type = action_type.lower()

        # Email actions
        if 'email' in action_type or 'send_email' in action_type:
            return self._execute_email(action, details)

        # LinkedIn post actions
        elif 'linkedin' in action_type or 'post' in action_type:
            return self._execute_linkedin_post(action, details)

        # WhatsApp actions
        elif 'whatsapp' in action_type or 'send_message' in action_type:
            return self._execute_whatsapp(action, details)

        # Generic/file actions
        elif 'file' in action_type or 'move' in action_type:
            return self._execute_file_action(action, details)

        # Generic approval (just mark as done)
        else:
            return {
                'success': True,
                'message': f"Generic action '{action_type}' approved and logged"
            }

    def _execute_email(self, action: dict, details: dict) -> dict:
        """Execute email send via helper"""
        try:
            to = details.get('to', '')
            subject = details.get('subject', 'No Subject')

            if not to or '@' not in to:
                return {'success': False, 'error': 'No valid recipient email found'}

            # Extract email body from approval content
            body = action.get('content', '')
            # Remove frontmatter
            if '---' in body:
                parts = body.split('---', 2)
                if len(parts) > 2:
                    body = parts[2].strip()

            result = subprocess.run(
                ['python', str(self.watchers_dir / 'email_mcp_helper.py'), 'send_email', to, subject, body[:1000]],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(self.watchers_dir)
            )

            if result.returncode == 0 and 'success' in result.stdout.lower():
                return {'success': True, 'message': f'Email sent to {to}'}
            else:
                return {'success': False, 'error': result.stderr or result.stdout or 'Email send failed'}

        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Email send timeout'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _execute_linkedin_post(self, action: dict, details: dict) -> dict:
        """Execute LinkedIn post via helper"""
        try:
            # Extract post content from approval
            content = action.get('content', '')
            # Remove frontmatter
            post_text = content
            if '---' in content:
                parts = content.split('---', 2)
                if len(parts) > 2:
                    post_text = parts[2].strip()

            # Limit to first 1000 chars for safety
            post_text = post_text[:1000]

            result = subprocess.run(
                ['python', str(self.watchers_dir / 'linkedin_mcp_helper.py'), 'create_post', post_text],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=str(self.watchers_dir)
            )

            if result.returncode == 0 and 'success' in result.stdout.lower():
                return {'success': True, 'message': 'LinkedIn post published'}
            else:
                return {'success': False, 'error': result.stderr or result.stdout or 'LinkedIn post failed'}

        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'LinkedIn post timeout'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _execute_whatsapp(self, action: dict, details: dict) -> dict:
        """Execute WhatsApp message via helper"""
        try:
            to = details.get('recipient', details.get('to', ''))
            message = details.get('message', details.get('text', ''))

            if not to or not message:
                return {'success': False, 'error': 'Missing recipient or message'}

            result = subprocess.run(
                ['python', str(self.watchers_dir / 'whatsapp_mcp_helper.py'), 'send_message', to, message],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=str(self.watchers_dir)
            )

            if result.returncode == 0 and 'success' in result.stdout.lower():
                return {'success': True, 'message': f'WhatsApp sent to {to}'}
            else:
                return {'success': False, 'error': result.stderr or result.stdout or 'WhatsApp send failed'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _execute_file_action(self, action: dict, details: dict) -> dict:
        """Execute file move/copy action"""
        try:
            source = details.get('source', '')
            dest = details.get('destination', details.get('dest', ''))

            if source and dest:
                src_path = Path(source)
                dest_path = Path(dest)

                if src_path.exists():
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(src_path), str(dest_path))
                    return {'success': True, 'message': f'File moved to {dest}'}
                else:
                    return {'success': False, 'error': f'Source file not found: {source}'}
            else:
                return {'success': True, 'message': 'File action logged (no paths specified)'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def reject_expired(self) -> list:
        """Move expired approvals to Rejected"""
        pending = self.check_pending()
        rejected = []

        for request in pending:
            if request['expired']:
                src = Path(request['path'])
                dest = self.rejected / request['file']
                shutil.move(str(src), str(dest))
                rejected.append(request['file'])
                self._log_approval(request['file'], 'expired', request['type'], {})

        return rejected

    def _log_approval(self, filename: str, action: str, request_type: str, details: dict):
        """Log approval action"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'file': filename,
            'action': action,
            'type': request_type,
            'details': details
        }

        with open(self.approval_log, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

    def get_history(self, days: int = 7) -> list:
        """Get approval history"""
        if not self.approval_log.exists():
            return []

        history = []
        cutoff = datetime.now() - timedelta(days=days)

        with open(self.approval_log, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    entry_time = datetime.fromisoformat(entry['timestamp'])
                    if entry_time >= cutoff:
                        history.append(entry)
                except:
                    continue

        return history

    def review_file(self, filename: str) -> str:
        """Review specific approval file"""
        for folder in [self.pending, self.approved, self.rejected, self.done]:
            filepath = folder / filename
            if filepath.exists():
                return filepath.read_text(encoding='utf-8')

        return f"File not found: {filename}"

    def monitor_approvals(self, interval: int = 30):
        """Continuous monitoring of Approved/ folder"""
        self.logger.info(f"Starting approval monitor (checking every {interval}s)")

        try:
            while True:
                results = self.execute_approved_actions()
                if results:
                    self.logger.info(f"Processed {len(results)} approved actions")
                import time
                time.sleep(interval)
        except KeyboardInterrupt:
            self.logger.info("Approval monitor stopped")


def main():
    parser = argparse.ArgumentParser(description='Approval Workflow for AI Employee')
    parser.add_argument('command', choices=['check', 'review', 'execute', 'request', 'history', 'cleanup', 'monitor'],
                       help='Command to execute')
    parser.add_argument('--vault', default=None, help='Path to vault')
    parser.add_argument('--file', default=None, help='Specific file to review')
    parser.add_argument('--type', default='generic', help='Approval request type')
    parser.add_argument('--details', default='', help='Request details (JSON)')
    parser.add_argument('--content', default='', help='Request content/context')
    parser.add_argument('--priority', choices=['high', 'medium', 'low'], default='medium')
    parser.add_argument('--days', type=int, default=7, help='History days')
    parser.add_argument('--interval', type=int, default=30, help='Monitor interval seconds')

    args = parser.parse_args()

    if args.vault:
        vault_path = Path(args.vault)
    else:
        vault_path = Path(__file__).parent.parent / 'AI_Employee_Vault'

    workflow = ApprovalWorkflow(str(vault_path))

    if args.command == 'check':
        pending = workflow.check_pending()

        if not pending:
            print("[OK] No pending approvals")
        else:
            print(f"Pending Approvals ({len(pending)}):\n")
            for req in pending:
                status = "EXPIRED" if req['expired'] else "PENDING"
                print(f"[{status}] {req['file']}")
                print(f"   Type: {req['type']} | Priority: {req['priority']}")
                if req['expires']:
                    print(f"   Expires: {req['expires']}")
                print()

        approved = workflow.check_approved()
        if approved:
            print(f"\n[READY] Approved Ready for Execution ({len(approved)}):")
            for action in approved:
                print(f"  [READY] {action['file']}")
            print("\nRun 'approval_workflow.py execute' to execute these actions")

    elif args.command == 'review':
        if not args.file:
            print("Error: --file required for review")
            sys.exit(1)

        content = workflow.review_file(args.file)
        print(content)

    elif args.command == 'execute':
        print("Executing approved actions...\n")
        results = workflow.execute_approved_actions()

        if not results:
            print("[OK] No approved actions to execute")
        else:
            success_count = sum(1 for r in results if r['success'])
            print(f"\n{'='*50}")
            print(f"Execution Complete: {success_count}/{len(results)} successful")
            print(f"{'='*50}")
            for result in results:
                if result['success']:
                    print(f"[OK] Executed: {result['file']}")
                else:
                    print(f"[FAIL] Failed: {result['file']}")
                    print(f"  Error: {result.get('error', 'Unknown error')}")

    elif args.command == 'request':
        details = {}
        if args.details:
            try:
                details = json.loads(args.details)
            except:
                print("Error: --details must be valid JSON")
                sys.exit(1)

        filepath = workflow.create_approval_request(args.type, details, args.content, args.priority)
        print(f"[OK] Approval request created: {filepath.name}")
        print(f"  Location: {filepath}")
        print(f"  Priority: {args.priority}")
        print(f"  Expires in {workflow.expiration_hours} hours")
        print(f"\nTo approve: Move file to Approved/ folder")
        print(f"To reject: Move file to Rejected/ folder")

    elif args.command == 'history':
        history = workflow.get_history(args.days)

        if not history:
            print(f"No approval history in last {args.days} days")
        else:
            print(f"Approval History (Last {args.days} days):\n")
            for entry in history[-20:]:
                print(f"{entry['timestamp'][:16]} | {entry['action']:10} | {entry['file']}")

    elif args.command == 'cleanup':
        rejected = workflow.reject_expired()
        if rejected:
            print(f"Moved {len(rejected)} expired approvals to Rejected:")
            for f in rejected:
                print(f"  - {f}")
        else:
            print("No expired approvals to clean up")

    elif args.command == 'monitor':
        print(f"Starting approval monitor (interval: {args.interval}s)")
        print("Press Ctrl+C to stop\n")
        workflow.monitor_approvals(args.interval)


if __name__ == '__main__':
    main()
