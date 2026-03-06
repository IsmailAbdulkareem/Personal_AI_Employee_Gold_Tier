#!/usr/bin/env python3
"""
Dashboard Updater - Updates Dashboard.md with completed work
Run this after processing tasks or executing approvals
"""
import sys
from pathlib import Path
from datetime import datetime
import re

class DashboardUpdater:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.dashboard = self.vault_path / 'Dashboard.md'
        self.done = self.vault_path / 'Done'
        self.plans = self.vault_path / 'Plans'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.needs_action = self.vault_path / 'Needs_Action'
        self.in_progress = self.vault_path / 'In_Progress'
        
    def update(self):
        """Update dashboard with current stats and completed work"""
        if not self.dashboard.exists():
            print("Dashboard.md not found!")
            return False
        
        # Count files
        stats = {
            'needs_action': len(list(self.needs_action.glob('*.md'))),
            'plans': len(list(self.plans.glob('*.md'))),
            'pending_approval': len(list(self.pending_approval.glob('*.md'))),
            'approved': len(list(self.approved.glob('*.md'))),
            'done': len(list(self.done.glob('*.md'))),
            'in_progress': len(list(self.in_progress.glob('*.md'))) if self.in_progress.exists() else 0
        }
        
        # Get today's completions
        today = datetime.now().strftime('%Y-%m-%d')
        done_today = 0
        recent = []
        
        for f in sorted(self.done.glob('*.md'), key=lambda x: x.stat().st_mtime, reverse=True):
            try:
                mtime = datetime.fromtimestamp(f.stat().st_mtime)
                if mtime.strftime('%Y-%m-%d') == today:
                    done_today += 1
                    recent.append({'file': f.name, 'time': mtime.strftime('%H:%M')})
            except:
                pass
        
        # Read dashboard
        content = self.dashboard.read_text(encoding='utf-8')
        
        # Update timestamp
        content = re.sub(
            r'last_updated: [^\n]+',
            f'last_updated: {datetime.now().isoformat()}Z',
            content
        )
        
        # Update table metrics
        replacements = {
            r'\| \*\*Pending Actions\*\* \|.*?\|': f'| **Pending Actions** | {stats["needs_action"]} | - |',
            r'\| \*\*In Progress\*\* \|.*?\|': f'| **In Progress** | {stats["in_progress"]} | - |',
            r'\| \*\*Awaiting Approval\*\* \|.*?\|': f'| **Awaiting Approval** | {stats["pending_approval"]} | - |',
            r'\| \*\*Approved \(Ready\)\*\* \|.*?\|': f'| **Approved (Ready)** | {stats["approved"]} | - |',
            r'\| \*\*Completed Today\*\* \|.*?\|': f'| **Completed Today** | {done_today} | {"+" + str(done_today) if done_today > 0 else "0"} |',
            r'\| \*\*Plans Created\*\* \|.*?\|': f'| **Plans Created** | {stats["plans"]} | - |',
            r'\| Files in Needs_Action \|.*?\|': f'| Files in Needs_Action | {stats["needs_action"]} |',
            r'\| Files in Plans \|.*?\|': f'| Files in Plans | {stats["plans"]} |',
            r'\| Files in Pending_Approval \|.*?\|': f'| Files in Pending_Approval | {stats["pending_approval"]} |',
            r'\| Files in Approved \|.*?\|': f'| Files in Approved | {stats["approved"]} |',
            r'\| Files in Done \(Today\) \|.*?\|': f'| Files in Done (Today) | {done_today} |',
            r'\| Files in Done \(Total\) \|.*?\|': f'| Files in Done (Total) | {stats["done"]} |',
        }
        
        for pattern, replacement in replacements.items():
            content = re.sub(pattern, replacement, content)
        
        # Update recent activity
        if recent:
            activity = "\n".join([f"- ✅ [{r['time']}] {r['file']}" for r in recent[:10]])
            content = re.sub(
                r'### Recent Activity\n\n\*No recent activity.*?\n',
                f'### Recent Activity\n\n{activity}\n\n',
                content,
                flags=re.DOTALL
            )
            content = re.sub(
                r'\*No recent activity\. System ready for tasks\.\*',
                f'{activity}\n\n',
                content
            )
        
        # Write back
        self.dashboard.write_text(content, encoding='utf-8')
        print(f"Dashboard updated: {stats['done']} total, {done_today} today")
        return True


if __name__ == '__main__':
    vault_path = Path(__file__).parent.parent / 'AI_Employee_Vault'
    updater = DashboardUpdater(str(vault_path))
    updater.update()
