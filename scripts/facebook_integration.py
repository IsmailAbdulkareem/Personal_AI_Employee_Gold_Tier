#!/usr/bin/env python3
"""
Facebook Integration for Gold Tier AI Employee

This script connects the Facebook MCP server to the AI Employee workflow.
It handles:
- Monitoring Facebook page
- Creating posts (with approval)
- Reading engagement metrics
"""
import sys
import os
import json
import subprocess
from pathlib import Path
from typing import Dict, Optional


class FacebookIntegration:
    """Facebook integration for AI Employee"""
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.mcp_server_path = Path(__file__).parent.parent / 'mcp-servers' / 'facebook-mcp'
        self.needs_action = self.vault_path / 'Needs_Action'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.done = self.vault_path / 'Done'
        self.logs = self.vault_path / 'Logs'
        
        # Ensure folders exist
        for folder in [self.needs_action, self.pending_approval, self.done, self.logs]:
            folder.mkdir(parents=True, exist_ok=True)
    
    def test_mcp_connection(self) -> bool:
        """Test if Facebook MCP server is working"""
        print("Testing Facebook MCP connection...")
        
        try:
            # Run test script
            result = subprocess.run(
                ['node', 'test-facebook.js'],
                cwd=self.mcp_server_path,
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8'
            )
            
            if 'FACEBOOK MCP SERVER - READY' in result.stdout:
                print("[OK] Facebook MCP server is connected and ready")
                return True
            else:
                print("[WARN] Facebook MCP server has issues")
                print(result.stdout)
                return False
                
        except Exception as e:
            print(f"[ERROR] Error testing MCP connection: {e}")
            return False
    
    def create_facebook_post(self, message: str, approval_required: bool = True) -> Dict:
        """
        Create a Facebook post (with approval workflow)
        
        Args:
            message: The post content
            approval_required: If True, creates approval request
            
        Returns:
            Status dictionary
        """
        print(f"\n[FACEBOOK] Creating Facebook post...")
        print(f"Message: {message[:100]}...")
        
        if approval_required:
            # Create approval request file
            return self._create_approval_request(message)
        else:
            # Post directly (not recommended)
            return self._post_direct(message)
    
    def _create_approval_request(self, message: str) -> Dict:
        """Create approval request file in Pending_Approval folder"""
        
        approval_file = self.pending_approval / f'FACEBOOK_POST_{Path(self.vault_path).name}.md'
        
        content = f"""---
type: facebook_post
action: facebook/post_message
status: pending
created: {Path(self.vault_path).name}
priority: medium
platform: Facebook
---

# Facebook Post Approval Request

## Post Content
```
{message}
```

## To Approve
1. Review the post content above
2. Move this file to `Approved/` folder to publish
3. Or move to `Rejected/` to cancel

## Details
- **Platform**: Facebook Page
- **Page ID**: {os.getenv('FB_PAGE_ID', 'N/A')}
- **Type**: Text Post
- **Requires**: pages_manage_posts permission

---
*Created by Gold Tier AI Employee*
"""
        
        approval_file.write_text(content, encoding='utf-8')
        
        print(f"[OK] Approval request created: {approval_file.name}")
        print(f"[INFO] Location: Pending_Approval/{approval_file.name}")
        print(f"[ACTION] Move to Approved/ to publish")
        
        return {
            'status': 'pending_approval',
            'file': str(approval_file),
            'message': message
        }
    
    def _post_direct(self, message: str) -> Dict:
        """Post directly to Facebook (bypasses approval - not recommended)"""
        
        print("[WARN] Posting directly to Facebook (no approval)...")
        
        # Call MCP server
        mcp_request = {
            "jsonrpc": "2.0",
            "method": "facebook/post_message",
            "params": {
                "message": message
            },
            "id": 1
        }
        
        try:
            # Start MCP server
            process = subprocess.Popen(
                ['node', 'index.js'],
                cwd=self.mcp_server_path,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8'
            )
            
            # Send request
            stdout, stderr = process.communicate(
                input=json.dumps(mcp_request) + '\n',
                timeout=30
            )
            
            # Parse response
            response = json.loads(stdout.strip())
            
            if 'result' in response and 'post_id' in response['result']:
                post_id = response['result']['post_id']
                print(f"[OK] Post published successfully: {post_id}")
                
                # Log the action
                self._log_action('facebook_post', message, {'post_id': post_id})
                
                return {
                    'status': 'posted',
                    'post_id': post_id,
                    'message': message
                }
            else:
                print(f"[ERROR] Post failed: {response}")
                return {
                    'status': 'failed',
                    'error': str(response)
                }
                
        except Exception as e:
            print(f"[ERROR] Error posting: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def get_page_info(self) -> Dict:
        """Get Facebook page information"""
        
        mcp_request = {
            "jsonrpc": "2.0",
            "method": "facebook/authenticate",
            "params": {},
            "id": 1
        }
        
        try:
            process = subprocess.Popen(
                ['node', 'index.js'],
                cwd=self.mcp_server_path,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(
                input=json.dumps(mcp_request) + '\n',
                timeout=30
            )
            
            response = json.loads(stdout.strip())
            return response.get('result', {})
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_recent_posts(self, limit: int = 5) -> Dict:
        """Get recent posts from Facebook page"""
        
        mcp_request = {
            "jsonrpc": "2.0",
            "method": "facebook/get_posts",
            "params": {
                "limit": limit
            },
            "id": 1
        }
        
        try:
            process = subprocess.Popen(
                ['node', 'index.js'],
                cwd=self.mcp_server_path,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(
                input=json.dumps(mcp_request) + '\n',
                timeout=30
            )
            
            response = json.loads(stdout.strip())
            return response.get('result', {})
            
        except Exception as e:
            return {'error': str(e)}
    
    def _log_action(self, action_type: str, message: str, details: Dict = None):
        """Log action to audit system"""
        
        log_file = self.logs / 'facebook_actions.jsonl'
        
        log_entry = {
            'timestamp': Path(self.vault_path).name,
            'action': action_type,
            'message': message[:100],
            'details': details or {}
        }
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')


def main():
    """Demo: Show how Facebook integration works"""
    
    print("="*70)
    print("FACEBOOK INTEGRATION DEMO - Gold Tier AI Employee")
    print("="*70)
    print()
    
    # Initialize
    vault_path = os.getenv('VAULT_PATH', 'AI_Employee_Vault_Gold_Tier')
    fb = FacebookIntegration(vault_path)
    
    # Step 1: Test Connection
    print("Step 1: Testing Facebook MCP Connection")
    print("-"*70)
    if fb.test_mcp_connection():
        print("[OK] Connection successful!")
    else:
        print("[ERROR] Connection failed - check your credentials")
        return
    print()
    
    # Step 2: Get Page Info
    print("Step 2: Getting Page Information")
    print("-"*70)
    page_info = fb.get_page_info()
    print(f"Page Info: {json.dumps(page_info, indent=2)}")
    print()
    
    # Step 3: Get Recent Posts
    print("Step 3: Getting Recent Posts")
    print("-"*70)
    posts = fb.get_recent_posts(3)
    print(f"Recent Posts: {json.dumps(posts, indent=2)}")
    print()
    
    # Step 4: Create Post (with approval)
    print("Step 4: Creating Facebook Post (Approval Workflow)")
    print("-"*70)
    test_message = "This is a test post from Gold Tier AI Employee! #AI #Automation"
    result = fb.create_facebook_post(test_message, approval_required=True)
    print(f"Result: {json.dumps(result, indent=2)}")
    print()
    
    # Summary
    print("="*70)
    print("HOW IT WORKS:")
    print("="*70)
    print("""
1. AI Employee detects need for Facebook post
   |
   +---> Creates approval request in Pending_Approval/
   
2. Human reviews approval request
   |
   +---> Moves file to Approved/ folder
   
3. Orchestrator executes approved action
   |
   +---> Calls Facebook MCP server
   +---> Post published to Facebook
   
4. Action logged and filed
   |
   +---> Logged in audit system
   +---> File moved to Done/
    
This ensures human oversight for all social media posts!
    """)
    print("="*70)


if __name__ == '__main__':
    main()
