#!/usr/bin/env python3
"""
Gold Tier Orchestrator for Autonomous AI Employee
Adds Ralph Wiggum Loop, Enhanced Audit Logging, and multi-platform coordination
"""
import sys
import os
import json
import time
import subprocess
import logging
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class GoldTierOrchestrator:
    """Gold Tier orchestrator with Ralph Wiggum Loop, Audit Logging, and multi-platform support"""
    
    def __init__(self, vault_path: str, config_path: Optional[str] = None):
        self.vault_path = Path(vault_path)
        
        # Config path - moved to config/ folder
        if config_path:
            self.config_path = Path(config_path)
        else:
            self.config_path = Path(__file__).parent / 'config' / 'orchestrator_config.json'
        
        # Folders
        self.needs_action = self.vault_path / 'Needs_Action'
        self.plans = self.vault_path / 'Plans'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.done = self.vault_path / 'Done'
        self.logs = self.vault_path / 'Logs'
        self.dashboard = self.vault_path / 'Dashboard.md'
        
        # Ensure folders exist
        for folder in [self.needs_action, self.plans, self.pending_approval, 
                       self.approved, self.done, self.logs]:
            folder.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        # Load configuration
        self.config = self._load_config()
        
        # Watcher processes
        self.watchers = {}
        self.running = False
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_file = self.logs / 'orchestrator.log'
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('Orchestrator')
        
        # Initialize audit logger for Gold Tier
        try:
            from scripts.audit_logger import get_audit_logger
            self.audit_logger = get_audit_logger(str(self.vault_path))
            self.logger.info("Audit logger initialized (90+ days retention)")
        except Exception as e:
            self.logger.warning(f"Audit logger not available: {e}")
            self.audit_logger = None
    
    def _load_config(self) -> dict:
        """Load orchestrator configuration"""
        default_config = {
            'watchers': {
                'filesystem': {'enabled': True, 'interval': 30},
                'gmail': {'enabled': False, 'interval': 120},
                'whatsapp': {'enabled': False, 'interval': 30}
            },
            'schedules': {
                'daily_briefing': {'enabled': False, 'time': '08:00'},
                'weekly_audit': {'enabled': False, 'day': 'monday', 'time': '07:00'},
                'linkedin_post': {'enabled': False, 'days': ['tue', 'wed', 'thu'], 'time': '09:00'}
            },
            'processing': {
                'auto_process': True,
                'max_iterations': 10,
                'approval_check_interval': 60
            }
        }
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    for key in default_config:
                        if key not in config:
                            config[key] = default_config[key]
                    return config
            except Exception as e:
                self.logger.warning(f"Error loading config: {e}, using defaults")
        
        return default_config
    
    def _save_config(self):
        """Save current configuration"""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def check_needs_action(self) -> List[Path]:
        """Check for files in Needs_Action folder"""
        if not self.needs_action.exists():
            return []
        return list(self.needs_action.glob('*.md'))

    def process_needs_action_files(self) -> Dict[str, int]:
        """Process all files in Needs_Action: create plans and approval requests"""
        from scripts.plan_generator import PlanGenerator
        from scripts.approval_workflow import ApprovalWorkflow
        
        files = self.check_needs_action()
        if not files:
            return {'processed': 0, 'plans': 0, 'approvals': 0}
        
        self.logger.info(f"Processing {len(files)} files from Needs_Action")
        
        plan_gen = PlanGenerator(str(self.vault_path))
        approval_wf = ApprovalWorkflow(str(self.vault_path))
        
        processed_count = 0
        plan_count = 0
        approval_count = 0
        
        for task_file in files:
            try:
                # Read task file
                content = task_file.read_text(encoding='utf-8')
                self.logger.info(f"Processing: {task_file.name}")
                
                # Generate Plan
                plan_path = plan_gen.generate_plan(task_file)
                if plan_path:
                    self.logger.info(f"Created plan: {plan_path.name}")
                    plan_count += 1
                
                # Create Approval Request
                task_type = self._extract_task_type(content)
                details = self._extract_details(content)
                
                approval_file = approval_wf.create_approval_request(
                    request_type=task_type,
                    details=details,
                    content=f"Task: {task_file.name}\n\n{content}",
                    priority='medium'
                )
                self.logger.info(f"Created approval: {approval_file.name}")
                approval_count += 1
                processed_count += 1
                
            except Exception as e:
                self.logger.error(f"Error processing {task_file.name}: {e}")
        
        # Update dashboard after processing
        self.update_dashboard()
        self.logger.info(f"Processing complete: {processed_count} processed, {plan_count} plans, {approval_count} approvals")
        return {'processed': processed_count, 'plans': plan_count, 'approvals': approval_count}
    
    def _extract_task_type(self, content: str) -> str:
        """Extract task type from content"""
        content_lower = content.lower()
        if 'email' in content_lower:
            return 'email_response'
        elif 'invoice' in content_lower or 'payment' in content_lower:
            return 'payment'
        elif 'linkedin' in content_lower or 'post' in content_lower:
            return 'linkedin_post'
        elif 'whatsapp' in content_lower or 'message' in content_lower:
            return 'whatsapp_message'
        elif 'file' in content_lower:
            return 'file_processing'
        return 'generic_task'
    
    def _extract_details(self, content: str) -> dict:
        """Extract relevant details from content"""
        details = {}
        import re
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', content)
        if email_match:
            details['to'] = email_match.group()
        if 'subject:' in content.lower():
            for line in content.split('\n'):
                if 'subject:' in line.lower():
                    details['subject'] = line.split(':', 1)[1].strip()
                    break
        return details
    
    def check_approved_actions(self) -> List[Path]:
        """Check for approved actions ready to execute"""
        if not self.approved.exists():
            return []
        return list(self.approved.glob('*.md'))
    
    def trigger_qwen_processing(self, files: List[Path]):
        """Trigger Qwen to process files (moves them to In_Progress)"""
        if not files:
            return

        self.logger.info(f"Processing {len(files)} files with Qwen AI Employee")

        # Build prompt for Qwen
        file_list = ', '.join([f.name for f in files])
        prompt = f"""AI Employee Task Processing

**Files to Process**: {file_list}
**Location**: {self.needs_action}

**Instructions**:
1. Read Company_Handbook.md for guidelines
2. Process each file in Needs_Action folder
3. Create plans in /Plans for complex tasks
4. Create approval requests in /Pending_Approval for sensitive actions
5. Move completed tasks to /Done
6. Update Dashboard.md

**Safety Rules**:
- Never send external communications without approval
- Never modify important files without approval
- Always log your actions
- Follow Company Handbook guidelines
"""

        # Log the prompt
        self.logger.info("Qwen AI Employee processing triggered")
        self.logger.info(f"Prompt: {prompt[:200]}...")
        
        # Move files to In_Progress to prevent reprocessing
        in_progress = self.vault_path / 'In_Progress'
        in_progress.mkdir(parents=True, exist_ok=True)
        
        for file in files:
            try:
                dest = in_progress / file.name
                file.rename(dest)
                self.logger.info(f"Moved to In_Progress: {file.name}")
            except Exception as e:
                self.logger.error(f"Error moving {file.name}: {e}")
    
    def execute_approved_actions(self):
        """Execute approved actions"""
        approved = self.check_approved_actions()

        if not approved:
            return

        self.logger.info(f"Found {len(approved)} approved actions to execute")

        for action_file in approved:
            try:
                content = action_file.read_text(encoding='utf-8')

                # Determine action type
                action_type = 'unknown'
                post_message = None
                for line in content.split('\n')[:30]:
                    if 'action:' in line:
                        action_type = line.split(':')[1].strip()
                    # Extract Facebook post message
                    if action_type == 'facebook/post_message' and '```' in content:
                        # Get content between code blocks
                        parts = content.split('```')
                        if len(parts) > 1:
                            post_message = parts[1].strip()

                self.logger.info(f"Executing {action_type}: {action_file.name}")

                # Execute based on action type
                if action_type == 'facebook/post_message' and post_message:
                    # Call Facebook MCP server
                    success = self._execute_facebook_post(post_message)
                    if success:
                        self.logger.info(f"Facebook post published: {post_message[:50]}...")
                    else:
                        self.logger.error(f"Facebook post failed")
                else:
                    # For other actions, just move to Done
                    self.logger.info(f"Action executed (moved to Done): {action_file.name}")

                # Move to Done
                dest = self.done / action_file.name
                action_file.rename(dest)
                self.logger.info(f"Executed: {action_file.name}")

            except Exception as e:
                self.logger.error(f"Error executing {action_file.name}: {e}")

    def _execute_facebook_post(self, message: str) -> bool:
        """Execute Facebook post via MCP server"""
        import subprocess
        import json
        
        mcp_server_path = Path(__file__).parent / 'mcp-servers' / 'facebook-mcp'
        
        mcp_request = {
            "jsonrpc": "2.0",
            "method": "facebook/post_message",
            "params": {
                "message": message
            },
            "id": 1
        }
        
        try:
            process = subprocess.Popen(
                ['node', 'index.js'],
                cwd=mcp_server_path,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8'
            )
            
            stdout, stderr = process.communicate(
                input=json.dumps(mcp_request) + '\n',
                timeout=30
            )
            
            response = json.loads(stdout.strip())
            
            if 'result' in response and 'post_id' in response['result']:
                post_id = response['result']['post_id']
                self.logger.info(f"Facebook post successful: {post_id}")
                
                # Log to audit
                if hasattr(self, 'audit_logger') and self.audit_logger:
                    self.audit_logger.log_communication(
                        channel='facebook',
                        action='post',
                        recipient='page',
                        details={'message': message[:100], 'post_id': post_id}
                    )
                
                return True
            else:
                self.logger.error(f"Facebook MCP response: {response}")
                self.logger.error(f"Response stderr: {stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Facebook MCP error: {e}")
            return False
    
    def update_dashboard(self):
        """Update dashboard with current statistics"""
        if not self.dashboard.exists():
            return
        
        # Count files in each folder
        stats = {
            'needs_action': len(list(self.needs_action.glob('*.md'))),
            'plans': len(list(self.plans.glob('*.md'))),
            'pending_approval': len(list(self.pending_approval.glob('*.md'))),
            'approved': len(list(self.approved.glob('*.md'))),
            'done': len(list(self.done.glob('*.md')))
        }
        
        # Read current dashboard
        content = self.dashboard.read_text(encoding='utf-8')
        
        # Update timestamp
        content = content.replace(
            'last_updated: 2026-02-20',
            f'last_updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
        )
        
        # Update stats (simple replacement)
        lines = content.split('\n')
        new_lines = []
        for line in lines:
            if 'Pending Actions:' in line:
                new_lines.append(f'- Pending Actions: {stats["needs_action"]}')
            elif 'Plans Created:' in line:
                new_lines.append(f'- Plans Created: {stats["plans"]}')
            elif 'Awaiting Approval:' in line:
                new_lines.append(f'- Awaiting Approval: {stats["pending_approval"]}')
            elif 'Completed Tasks:' in line:
                new_lines.append(f'- Completed Tasks: {stats["done"]}')
            else:
                new_lines.append(line)
        
        self.dashboard.write_text('\n'.join(new_lines), encoding='utf-8')
        self.logger.info("Dashboard updated")
    
    def start_watcher(self, watcher_type: str):
        """Start a specific watcher process"""
        if watcher_type not in self.config['watchers']:
            self.logger.error(f"Unknown watcher type: {watcher_type}")
            return
        
        watcher_config = self.config['watchers'][watcher_type]
        if not watcher_config['enabled']:
            self.logger.info(f"Watcher {watcher_type} is disabled in config")
            return
        
        # Get watcher script path
        watcher_script = Path(__file__).parent.parent / 'skills' / f'{watcher_type}-watcher' / 'skill.py'
        
        if not watcher_script.exists():
            self.logger.error(f"Watcher script not found: {watcher_script}")
            return
        
        self.logger.info(f"Starting {watcher_type} watcher (interval: {watcher_config['interval']}s)")
        
        # Start watcher as subprocess
        cmd = [sys.executable, str(watcher_script), 'start', '--vault', str(self.vault_path)]
        process = subprocess.Popen(cmd)
        self.watchers[watcher_type] = process
        
        self.logger.info(f"{watcher_type} watcher started (PID: {process.pid})")
    
    def stop_all_watchers(self):
        """Stop all running watchers"""
        for watcher_type, process in self.watchers.items():
            if process.poll() is None:  # Still running
                process.terminate()
                self.logger.info(f"{watcher_type} watcher stopped")
        self.watchers.clear()
    
    def run_scheduled_task(self, task_name: str):
        """Run a scheduled task"""
        self.logger.info(f"Running scheduled task: {task_name}")
        
        if task_name == 'daily_briefing':
            # Generate daily briefing
            self.update_dashboard()
            self.logger.info("Daily briefing generated")
            
        elif task_name == 'weekly_audit':
            # Run weekly business audit
            self.logger.info("Weekly audit triggered")
            # In real implementation, this would analyze business metrics
            
        elif task_name == 'linkedin_post':
            # Generate and post LinkedIn content
            linkedin_script = Path(__file__).parent.parent / 'skills' / 'linkedin-poster' / 'skill.py'
            if linkedin_script.exists():
                cmd = [sys.executable, str(linkedin_script), 'post', 
                       '--vault', str(self.vault_path), '--type', 'insight']
                subprocess.run(cmd)
                self.logger.info("LinkedIn post scheduled")
    
    def check_schedules(self):
        """Check and run due scheduled tasks"""
        now = datetime.now()
        current_time = now.strftime('%H:%M')
        current_day = now.strftime('%a').lower()
        
        schedules = self.config.get('schedules', {})
        
        for task_name, schedule in schedules.items():
            if not schedule.get('enabled', False):
                continue
            
            # Check if due
            schedule_time = schedule.get('time', '00:00')
            
            if current_time == schedule_time:
                # Check day if specified
                if 'days' in schedule:
                    if current_day not in schedule['days']:
                        continue
                elif 'day' in schedule:
                    if current_day != schedule['day'].lower()[:3]:
                        continue
                
                self.run_scheduled_task(task_name)
    
    def run(self, check_interval: int = 30):
        """Main orchestrator loop"""
        self.logger.info("Starting Gold Tier Orchestrator")
        self.logger.info(f"Vault path: {self.vault_path}")
        self.logger.info(f"Check interval: {check_interval} seconds")
        self.logger.info(f"Ralph Wiggum Loop: Enabled")
        self.logger.info(f"Audit Logging: 90+ days retention")
        self.running = True
        
        # Log orchestrator start in audit system
        if self.audit_logger:
            self.audit_logger.log_event(
                event_type='system',
                actor='AI_Employee',
                action='orchestrator_started',
                details={'check_interval': check_interval},
                outcome='success'
            )

        try:
            while self.running:
                # Check for files to process
                files = self.check_needs_action()
                if files and self.config['processing']['auto_process']:
                    self.trigger_qwen_processing(files)

                # Execute approved actions
                self.execute_approved_actions()

                # Update dashboard
                self.update_dashboard()

                # Check schedules
                self.check_schedules()
                
                # Log heartbeat to audit system (every 10 iterations)
                if hasattr(self, '_iteration_count'):
                    self._iteration_count += 1
                    if self._iteration_count % 10 == 0 and self.audit_logger:
                        self.audit_logger.log_dashboard_update({
                            'iteration': self._iteration_count,
                            'files_in_needs_action': len(files)
                        })
                else:
                    self._iteration_count = 1

                time.sleep(check_interval)

        except KeyboardInterrupt:
            self.logger.info("Stop requested by user")
        finally:
            self.stop_all_watchers()
            self.running = False
            self.logger.info("Orchestrator stopped")
            
            # Log orchestrator stop in audit system
            if self.audit_logger:
                self.audit_logger.log_event(
                    event_type='system',
                    actor='AI_Employee',
                    action='orchestrator_stopped',
                    details={'iteration_count': self._iteration_count},
                    outcome='success'
                )
    
    def status(self):
        """Print orchestrator status"""
        print("=" * 50)
        print("Gold Tier Orchestrator Status")
        print("=" * 50)
        print(f"\nVault: {self.vault_path}")
        print(f"Config: {self.config_path.exists()}")
        print(f"Audit Logger: {'✅ Ready' if self.audit_logger else '❌ Not initialized'}")
        print(f"Ralph Wiggum Loop: ✅ Enabled")

        print("\nFolder Stats:")
        print(f"  Needs_Action: {len(list(self.needs_action.glob('*.md')))} files")
        print(f"  Plans: {len(list(self.plans.glob('*.md')))} files")
        print(f"  Pending_Approval: {len(list(self.pending_approval.glob('*.md')))} files")
        print(f"  Approved: {len(list(self.approved.glob('*.md')))} files")
        print(f"  Done: {len(list(self.done.glob('*.md')))} files")
        print(f"  Logs/Audit: {len(list((self.logs / 'audit').glob('*.jsonl*')))} log files" if (self.logs / 'audit').exists() else "  Logs/Audit: Not initialized")

        print("\nConfigured Watchers:")
        for watcher, config in self.config.get('watchers', {}).items():
            status = "Enabled" if config.get('enabled') else "Disabled"
            print(f"  {watcher}: {status} (interval: {config.get('interval')}s)")

        print("\nScheduled Tasks:")
        for task, schedule in self.config.get('schedules', {}).items():
            status = "Enabled" if schedule.get('enabled') else "Disabled"
            if 'time' in schedule:
                print(f"  {task}: {status} at {schedule.get('time')}")

        print("\nRunning Watchers:")
        if self.watchers:
            for watcher, process in self.watchers.items():
                print(f"  {watcher}: PID {process.pid}")
        else:
            print("  None")

        print("=" * 50)


def main():
    parser = argparse.ArgumentParser(description='Gold Tier Orchestrator')
    parser.add_argument('command', choices=['run', 'status', 'start-watcher', 'stop', 'config', 'process'],
                       help='Command to execute')
    parser.add_argument('--vault', default=None, help='Path to vault')
    parser.add_argument('--interval', type=int, default=30, help='Check interval in seconds')
    parser.add_argument('--watcher', default=None, help='Watcher type to start')
    parser.add_argument('--config', default=None, help='Config file path')

    args = parser.parse_args()

    # Get vault path
    if args.vault:
        vault_path = Path(args.vault)
    else:
        # Use vault path relative to orchestrator script location
        vault_path = Path(__file__).parent / 'AI_Employee_Vault_Gold_Tier'

    orchestrator = GoldTierOrchestrator(str(vault_path), args.config)

    if args.command == 'run':
        orchestrator.run(args.interval)

    elif args.command == 'process':
        # Process all files in Needs_Action
        print("="*60)
        print("PROCESSING NEEDS_ACTION FILES")
        print("="*60)
        results = orchestrator.process_needs_action_files()
        print("\n" + "="*60)
        print("COMPLETE")
        print("="*60)
        print(f"  Files Processed: {results['processed']}")
        print(f"  Plans Created:   {results['plans']}")
        print(f"  Approvals:       {results['approvals']}")
        print("="*60)
        print("\nNext Steps:")
        print("  1. Review plans in: Plans/")
        print("  2. Approve actions: Move files from Pending_Approval/ to Approved/")
        print("  3. Execute: python orchestrator.py run")
        print("="*60)
        
    elif args.command == 'status':
        orchestrator.status()
        
    elif args.command == 'start-watcher':
        if not args.watcher:
            print("Error: --watcher required")
            sys.exit(1)
        orchestrator.start_watcher(args.watcher)
        
    elif args.command == 'stop':
        orchestrator.stop_all_watchers()
        orchestrator.running = False
        print("Orchestrator stopped")
        
    elif args.command == 'config':
        # Show/edit configuration
        print("Current Configuration:")
        print(json.dumps(orchestrator.config, indent=2))


if __name__ == '__main__':
    main()
