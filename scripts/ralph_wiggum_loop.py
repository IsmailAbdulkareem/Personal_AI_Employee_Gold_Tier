#!/usr/bin/env python3
"""
Ralph Wiggum Stop Hook for Gold Tier AI Employee

This plugin intercepts Claude Code's exit attempts and keeps it working
until tasks are complete. Implements autonomous multi-step task completion.

Reference: https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum
"""
import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any


class RalphWiggumStopHook:
    """
    Stop hook that prevents Claude from exiting until tasks are complete.
    
    Two completion strategies:
    1. Promise-based: Claude outputs <promise>TASK_COMPLETE</promise>
    2. File movement: Task file moved to /Done folder
    """
    
    def __init__(
        self,
        vault_path: str,
        max_iterations: int = 10,
        completion_promise: str = "TASK_COMPLETE",
        state_file_path: Optional[str] = None
    ):
        self.vault_path = Path(vault_path)
        self.max_iterations = max_iterations
        self.completion_promise = completion_promise
        self.state_file_path = state_file_path or self.vault_path / 'In_Progress' / 'ralph_state.json'
        self.iteration_count = 0
        self.start_time = datetime.now()
        
        # Ensure state directory exists
        self.state_file_path.parent.mkdir(parents=True, exist_ok=True)
        
    def load_state(self) -> Dict[str, Any]:
        """Load current state from file"""
        if self.state_file_path.exists():
            with open(self.state_file_path, 'r') as f:
                return json.load(f)
        return {
            'task': '',
            'prompt': '',
            'iteration': 0,
            'started': datetime.now().isoformat(),
            'last_output': '',
            'errors': [],
            'status': 'pending'
        }
    
    def save_state(self, state: Dict[str, Any]):
        """Save current state to file"""
        with open(self.state_file_path, 'w') as f:
            json.dump(state, f, indent=2)
    
    def check_completion_promise(self, output: str) -> bool:
        """Check if output contains completion promise"""
        return f'<promise>{self.completion_promise}</promise>' in output
    
    def check_file_movement(self, task_file: str) -> bool:
        """Check if task file has been moved to /Done"""
        done_folder = self.vault_path / 'Done'
        return (done_folder / task_file).exists()
    
    def check_task_complete(self, state: Dict[str, Any], output: str) -> bool:
        """Check if task is complete using any strategy"""
        # Strategy 1: Completion promise
        if self.check_completion_promise(output):
            return True
        
        # Strategy 2: File movement
        task_file = state.get('task_file', '')
        if task_file and self.check_file_movement(task_file):
            return True
        
        # Strategy 3: Explicit status in state
        if state.get('status') == 'complete':
            return True
        
        return False
    
    def should_allow_exit(self, output: str) -> bool:
        """
        Determine if Claude should be allowed to exit.
        
        Returns True if:
        - Task is complete
        - Max iterations reached
        - Error state detected
        
        Returns False to continue loop
        """
        state = self.load_state()
        self.iteration_count = state.get('iteration', 0)
        
        # Check max iterations
        if self.iteration_count >= self.max_iterations:
            self.log_error(f"Max iterations ({self.max_iterations}) reached")
            return True
        
        # Check task completion
        if self.check_task_complete(state, output):
            state['status'] = 'complete'
            state['completed'] = datetime.now().isoformat()
            self.save_state(state)
            return True
        
        # Check for critical errors
        if 'CRITICAL_ERROR' in output or 'FATAL' in output:
            self.log_error("Critical error detected in output")
            return True
        
        return False
    
    def log_error(self, error: str):
        """Log error to state"""
        state = self.load_state()
        state['errors'].append({
            'timestamp': datetime.now().isoformat(),
            'error': error
        })
        self.save_state(state)
    
    def create_reinject_prompt(self, state: Dict[str, Any], output: str) -> str:
        """Create prompt to re-inject for next iteration"""
        self.iteration_count += 1
        
        # Update state
        state['iteration'] = self.iteration_count
        state['last_output'] = output
        state['last_updated'] = datetime.now().isoformat()
        state['status'] = 'in_progress'
        self.save_state(state)
        
        # Build reinjection prompt
        prompt = f"""
[RALPH WIGGUM LOOP - Iteration {self.iteration_count}/{self.max_iterations}]

**Task Status**: INCOMPLETE - Continue working

**Original Task**: {state.get('task', 'Unknown')}

**Previous Output Analysis**:
Your last attempt did not complete the task. Review what you did and try a different approach.

**Instructions**:
1. Review your previous output above
2. Identify what prevented task completion
3. Try a different strategy or approach
4. Continue working until the task is complete
5. Output <promise>TASK_COMPLETE</promise> when done

**State File**: {self.state_file_path}
**Vault Path**: {self.vault_path}

Continue working on the task now.
"""
        return prompt
    
    def intercept_exit(self, output: str) -> tuple[bool, Optional[str]]:
        """
        Intercept exit attempt.
        
        Returns:
            (allow_exit, reinject_prompt)
            - If allow_exit is True, reinject_prompt is None
            - If allow_exit is False, reinject_prompt contains next prompt
        """
        if self.should_allow_exit(output):
            return True, None
        
        reinject_prompt = self.create_reinject_prompt(output)
        return False, reinject_prompt
    
    def run_loop(self, initial_prompt: str):
        """
        Run the Ralph Wiggum loop with initial prompt.
        
        This is the main entry point for autonomous task execution.
        """
        state = {
            'task': initial_prompt,
            'prompt': initial_prompt,
            'iteration': 0,
            'started': datetime.now().isoformat(),
            'last_output': '',
            'errors': [],
            'status': 'pending'
        }
        self.save_state(state)
        
        print(f"[RALPH WIGGUM] Starting autonomous task loop")
        print(f"[RALPH WIGGUM] Max iterations: {self.max_iterations}")
        print(f"[RALPH WIGGUM] Vault path: {self.vault_path}")
        print(f"[RALPH WIGGUM] State file: {self.state_file_path}")
        print()


def main():
    """CLI entry point for Ralph Wiggum loop"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Ralph Wiggum Stop Hook')
    parser.add_argument('prompt', help='Task prompt to execute')
    parser.add_argument('--vault', default=None, help='Path to vault')
    parser.add_argument('--max-iterations', type=int, default=10, help='Max iterations')
    parser.add_argument('--completion-promise', default='TASK_COMPLETE', help='Completion promise tag')
    parser.add_argument('--state-file', default=None, help='State file path')
    
    args = parser.parse_args()
    
    vault_path = args.vault or os.environ.get('VAULT_PATH', '.')
    
    ralph = RalphWiggumStopHook(
        vault_path=vault_path,
        max_iterations=args.max_iterations,
        completion_promise=args.completion_promise,
        state_file_path=args.state_file
    )
    
    ralph.run_loop(args.prompt)
    
    print(f"[RALPH WIGGUM] Loop initialized. Ready for task execution.")
    print(f"[RALPH WIGGUM] Use intercept_exit() to monitor Claude's exit attempts.")


if __name__ == '__main__':
    main()
