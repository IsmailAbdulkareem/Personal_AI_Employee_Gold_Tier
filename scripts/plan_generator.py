#!/usr/bin/env python3
"""
Plan Generator Skill for AI Employee
Creates detailed action plans for tasks using reasoning
"""
import sys
import argparse
from pathlib import Path
from datetime import datetime

class PlanGenerator:
    """Generate structured action plans for tasks"""
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.plans = self.vault_path / 'Plans'
        
        self.plan_templates = {
            'email_response': self._email_response_plan,
            'invoice_request': self._invoice_request_plan,
            'client_onboarding': self._client_onboarding_plan,
            'document_processing': self._document_processing_plan,
            'generic': self._generic_plan
        }
    
    def _detect_task_type(self, content: str) -> str:
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['email', 'reply', 'respond', 'message']):
            return 'email_response'
        elif any(word in content_lower for word in ['invoice', 'payment', 'bill', 'receipt']):
            return 'invoice_request'
        elif any(word in content_lower for word in ['client', 'onboard', 'new client', 'welcome']):
            return 'client_onboarding'
        elif any(word in content_lower for word in ['document', 'file', 'process', 'analyze']):
            return 'document_processing'
        else:
            return 'generic'
    
    def _estimate_effort(self, task_type: str) -> str:
        effort_map = {
            'email_response': '15 minutes',
            'invoice_request': '30 minutes',
            'client_onboarding': '2 hours',
            'document_processing': '45 minutes',
            'generic': '30 minutes'
        }
        return effort_map.get(task_type, '30 minutes')
    
    def _detect_priority(self, content: str) -> str:
        content_lower = content.lower()
        
        high_priority_keywords = ['urgent', 'asap', 'immediate', 'emergency', 'critical']
        medium_priority_keywords = ['soon', 'important', 'priority', 'deadline']
        
        if any(keyword in content_lower for keyword in high_priority_keywords):
            return 'high'
        elif any(keyword in content_lower for keyword in medium_priority_keywords):
            return 'medium'
        else:
            return 'medium'
    
    def _email_response_plan(self, task_file: str, content: str) -> str:
        return f"""---
type: action_plan
task_id: {Path(task_file).stem}
created: {datetime.now().isoformat()}
status: pending
priority: {self._detect_priority(content)}
estimated_effort: {self._estimate_effort('email_response')}
---

# Action Plan: Email Response

## Objective
Craft and send appropriate email response.

## Steps

### Phase 1: Analysis
- [ ] Read and understand email content
- [ ] Identify sender's needs/concerns
- [ ] Determine appropriate response tone

### Phase 2: Draft Response
- [ ] Write professional email draft
- [ ] Proofread for clarity and tone

### Phase 3: Approval
- [ ] Create approval file in /Pending_Approval/
- [ ] Wait for human approval

### Phase 4: Send
- [ ] Send approved email
- [ ] Log action

## Success Criteria
- Response sent within 24 hours
- All sender questions addressed
"""

    def _invoice_request_plan(self, task_file: str, content: str) -> str:
        return f"""---
type: action_plan
task_id: {Path(task_file).stem}
created: {datetime.now().isoformat()}
status: pending
priority: {self._detect_priority(content)}
estimated_effort: {self._estimate_effort('invoice_request')}
---

# Action Plan: Invoice Generation

## Objective
Generate professional invoice and send to client.

## Steps

### Phase 1: Information Gathering
- [ ] Identify client details
- [ ] Determine service period
- [ ] Calculate hours/amount due

### Phase 2: Invoice Creation
- [ ] Fill in client information
- [ ] Add line items
- [ ] Generate PDF

### Phase 3: Approval
- [ ] Create approval request
- [ ] Wait for approval

### Phase 4: Send
- [ ] Send invoice via email
- [ ] Log transaction

## Success Criteria
- Invoice accurate and professional
- Sent within 24 hours
"""

    def _client_onboarding_plan(self, task_file: str, content: str) -> str:
        return f"""---
type: action_plan
task_id: {Path(task_file).stem}
created: {datetime.now().isoformat()}
status: pending
priority: high
estimated_effort: {self._estimate_effort('client_onboarding')}
---

# Action Plan: Client Onboarding

## Objective
Complete full client onboarding process.

## Steps

### Phase 1: Welcome
- [ ] Send welcome email
- [ ] Schedule kickoff meeting

### Phase 2: Documentation
- [ ] Send service agreement
- [ ] Collect signed contract

### Phase 3: Setup
- [ ] Create client in CRM
- [ ] Set up billing

### Phase 4: Kickoff
- [ ] Conduct kickoff meeting
- [ ] Set first milestones

## Success Criteria
- All documentation complete
- First deliverable scheduled
"""

    def _document_processing_plan(self, task_file: str, content: str) -> str:
        return f"""---
type: action_plan
task_id: {Path(task_file).stem}
created: {datetime.now().isoformat()}
status: pending
priority: {self._detect_priority(content)}
estimated_effort: {self._estimate_effort('document_processing')}
---

# Action Plan: Document Processing

## Objective
Process and analyze document content.

## Steps

### Phase 1: Review
- [ ] Read document thoroughly
- [ ] Identify document type

### Phase 2: Analysis
- [ ] Extract relevant data
- [ ] Identify required actions

### Phase 3: Action
- [ ] Execute required actions
- [ ] File document

### Phase 4: Completion
- [ ] Log processing details
- [ ] Move to /Done/

## Success Criteria
- Document fully processed
- All actions completed
"""

    def _generic_plan(self, task_file: str, content: str) -> str:
        return f"""---
type: action_plan
task_id: {Path(task_file).stem}
created: {datetime.now().isoformat()}
status: pending
priority: {self._detect_priority(content)}
estimated_effort: {self._estimate_effort('generic')}
---

# Action Plan: Task Processing

## Objective
Complete task according to guidelines.

## Steps

### Phase 1: Understand
- [ ] Read task requirements
- [ ] Identify desired outcome

### Phase 2: Plan
- [ ] Break down into steps
- [ ] Identify dependencies

### Phase 3: Execute
- [ ] Complete safe actions
- [ ] Request approval for sensitive actions

### Phase 4: Complete
- [ ] Verify task completion
- [ ] Move to /Done/

## Success Criteria
- Task completed successfully
- All guidelines followed
"""

    def generate_plan(self, task_file: Path) -> Path:
        """Generate plan for a task file"""
        content = task_file.read_text(encoding='utf-8')
        task_type = self._detect_task_type(content)
        
        template_func = self.plan_templates.get(task_type, self._generic_plan)
        plan_content = template_func(str(task_file), content)
        
        self.plans.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        plan_filename = f"PLAN_{task_file.stem}_{timestamp}.md"
        plan_path = self.plans / plan_filename
        
        plan_path.write_text(plan_content, encoding='utf-8')
        
        return plan_path
    
    def generate_all_plans(self) -> list:
        """Generate plans for all tasks in Needs_Action"""
        if not self.needs_action.exists():
            return []
        
        generated = []
        for task_file in self.needs_action.glob('*.md'):
            try:
                plan_path = self.generate_plan(task_file)
                generated.append(plan_path)
                print(f"Generated plan: {plan_path.name}")
            except Exception as e:
                print(f"Error generating plan for {task_file.name}: {e}")
        
        return generated
    
    def review_plans(self):
        """Review existing plans"""
        if not self.plans.exists():
            print("No plans found")
            return
        
        plans = list(self.plans.glob('*.md'))
        print(f"Found {len(plans)} plans:\n")
        
        for plan in sorted(plans, key=lambda x: x.stat().st_mtime, reverse=True):
            content = plan.read_text(encoding='utf-8')
            
            status = "unknown"
            priority = "unknown"
            for line in content.split('\n')[:15]:
                if 'status:' in line:
                    status = line.split(':')[1].strip()
                if 'priority:' in line:
                    priority = line.split(':')[1].strip()
            
            print(f"[{status}] {plan.name} (Priority: {priority})")


def main():
    parser = argparse.ArgumentParser(description='Plan Generator for AI Employee')
    parser.add_argument('command', choices=['generate', 'review', 'update'],
                       help='Command to execute')
    parser.add_argument('--vault', default=None, help='Path to vault')
    parser.add_argument('--file', default=None, help='Specific task file to plan')
    
    args = parser.parse_args()
    
    if args.vault:
        vault_path = Path(args.vault)
    else:
        vault_path = Path(__file__).parent.parent / 'AI_Employee_Vault'
    
    generator = PlanGenerator(str(vault_path))
    
    if args.command == 'generate':
        if args.file:
            task_file = generator.needs_action / args.file
            if task_file.exists():
                plan_path = generator.generate_plan(task_file)
                print(f"Generated plan: {plan_path.name}")
            else:
                print(f"Task file not found: {task_file}")
                sys.exit(1)
        else:
            print("Generating plans for all tasks in Needs_Action...\n")
            generated = generator.generate_all_plans()
            print(f"\nGenerated {len(generated)} plans")
            
    elif args.command == 'review':
        generator.review_plans()


if __name__ == '__main__':
    main()
