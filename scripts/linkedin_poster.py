#!/usr/bin/env python3
"""
LinkedIn Poster Skill for AI Employee
Creates and posts business content to LinkedIn automatically
"""
import sys
import os
import json
import time
import logging
import random
import codecs
from pathlib import Path
from datetime import datetime, timedelta
import argparse

# Fix Windows console Unicode
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

SESSION_PATH = Path.home() / '.linkedin_session'
LOG_FILE = Path(__file__).parent.parent / 'AI_Employee_Vault' / 'Logs' / 'linkedin_posts.log'
MAX_POSTS_PER_DAY = 3
WAIT_TIMEOUT = 30000

class LinkedInPoster:
    """Create and post business content to LinkedIn"""
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.done = self.vault_path / 'Done'
        self.browser = None
        self.page = None
        
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()]
        )
        self.logger = logging.getLogger('LinkedInPoster')
        
        self.templates = {
            'milestone': self._generate_milestone_post,
            'insight': self._generate_insight_post,
            'success': self._generate_success_post,
            'update': self._generate_update_post
        }
        
        if not PLAYWRIGHT_AVAILABLE:
            self.logger.error("Playwright not installed. Run: pip install playwright && playwright install chromium")
    
    def _generate_milestone_post(self, topic: str = "") -> str:
        return f"""🎉 Exciting Milestone Alert!

I'm thrilled to share that we've just achieved a significant milestone.

{topic if topic else "This accomplishment reflects our commitment to excellence."}

Key highlights:
✅ Dedicated teamwork
✅ Client-focused approach
✅ Measurable results

#BusinessGrowth #Milestone #Success"""

    def _generate_insight_post(self, topic: str = "") -> str:
        return f"""💡 Industry Insight

After working extensively in the field, I've observed:

{topic if topic else "The most successful businesses prioritize automation over manual processes."}

Key takeaways:
• Focus on value delivery
• Embrace technology
• Measure what matters

#ThoughtLeadership #BusinessStrategy #Innovation"""

    def _generate_success_post(self, topic: str = "") -> str:
        return f"""⭐ Client Success Story

Another win for our clients! 🚀

{topic if topic else "We recently helped a client transform their operations."}

Results achieved:
📈 Significant efficiency gain
💰 Cost reduction
⏰ Time savings

#ClientSuccess #Results #ROI"""

    def _generate_update_post(self, topic: str = "") -> str:
        return f"""📢 Business Update

Quick update from our end:

{topic if topic else "We're expanding our services to better serve our clients."}

Excited about what's ahead!

#BusinessUpdate #Growth #Innovation"""

    def generate_post(self, post_type: str = "update", topic: str = "") -> str:
        template_func = self.templates.get(post_type, self._generate_update_post)
        return template_func(topic)
    
    def authenticate(self):
        """Launch browser and authenticate with LinkedIn"""
        if not PLAYWRIGHT_AVAILABLE:
            self.logger.error("Cannot authenticate: Playwright not available")
            return False
        
        try:
            self.playwright = sync_playwright().start()
            
            # Launch browser with persistent context (visible for interaction)
            self.browser = self.playwright.chromium.launch_persistent_context(
                str(SESSION_PATH),
                headless=False,  # Keep visible for user to see what's happening
                args=['--disable-blink-features=AutomationControlled', '--no-sandbox'],
                viewport={'width': 1280, 'height': 800}
            )
            
            self.page = self.browser.pages[0]

            self.logger.info("Navigating to LinkedIn...")
            self.page.goto('https://www.linkedin.com/login', wait_until='networkidle')

            print("\n" + "="*60)
            print("LINKEDIN AUTHENTICATION")
            print("="*60)
            print("\nA browser window has opened to LinkedIn.")
            print("Please log in with your LinkedIn credentials:")
            print("  1. Enter your email and password")
            print("  2. Complete any verification")
            print("  3. Once logged in, the script will continue automatically")
            print("\nWaiting for login (5 minutes)...")
            print("="*60 + "\n")

            # Wait for user to log in
            try:
                # Wait for feed to appear (indicates successful login)
                self.page.wait_for_selector('[data-id="feed"]', timeout=300000)
                self.logger.info("LinkedIn authenticated successfully!")
                print("\n✓ Authentication successful!")
                print("Session saved. Future runs will be automatic.\n")
                return True
            except Exception as e:
                self.logger.error(f"Authentication timeout: {e}")
                print("\n✗ Authentication timeout or failed.")
                print("Please try again.\n")
                return False
                    
        except Exception as e:
            self.logger.error(f"Authentication error: {e}")
            return False
    
    def create_draft(self, content: str, topic: str = "") -> Path:
        """Create draft post in Pending_Approval folder"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        content_md = f"""---
type: linkedin_post
topic: {topic if topic else 'business update'}
created: {datetime.now().isoformat()}
status: pending_approval
---

# LinkedIn Post Draft

**Topic:** {topic if topic else 'General Business Update'}

---

{content}

---

## Instructions
- Move to `/Approved` to publish
- Move to `/Rejected` to discard

*Generated by AI Employee - LinkedIn Poster*
"""
        
        self.pending_approval.mkdir(parents=True, exist_ok=True)
        safe_topic = "".join(c if c.isalnum() else "_" for c in (topic if topic else "update")[:30])
        filename = f"LINKEDIN_POST_{timestamp}_{safe_topic}.md"
        filepath = self.pending_approval / filename
        filepath.write_text(content_md, encoding='utf-8')
        
        self.logger.info(f"Created draft: {filepath.name}")
        return filepath
    
    def check_approved_posts(self) -> list:
        """Check for approved posts ready to publish"""
        if not self.approved.exists():
            return []
        
        approved_files = []
        for f in self.approved.glob('LINKEDIN_POST_*.md'):
            content = f.read_text(encoding='utf-8')
            if 'type: linkedin_post' in content:
                approved_files.append(f)
        
        return approved_files
    
    def extract_post_content(self, filepath: Path) -> str:
        """Extract post content from approved file"""
        content = filepath.read_text(encoding='utf-8')
        parts = content.split('---')
        if len(parts) >= 3:
            return parts[1].strip()
        return content
    
    def post_to_linkedin(self, content: str) -> bool:
        """Post content to LinkedIn"""
        if not self.page:
            return False
        
        try:
            if 'feed' not in self.page.url:
                self.page.goto('https://www.linkedin.com/feed/', wait_until='networkidle')
            
            self.page.wait_for_selector('[aria-label="Start a post"]', timeout=10000)
            self.page.click('[aria-label="Start a post"]')
            
            self.page.wait_for_selector('[contenteditable="true"]', timeout=10000)
            
            editor = self.page.query_selector('[contenteditable="true"]')
            if editor:
                editor.fill('')
                editor.type(content, delay=50)
                time.sleep(1)
                
                post_button = self.page.query_selector('button:has-text("Post")')
                if post_button:
                    post_button.click()
                    time.sleep(2)
                    
                    if 'feed' in self.page.url:
                        self.logger.info("Post published successfully!")
                        return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error posting to LinkedIn: {e}")
            return False
    
    def log_post(self, filepath: Path, success: bool):
        """Log post publication"""
        log_entry = {'timestamp': datetime.now().isoformat(), 'file': filepath.name, 'success': success}
        log_file = self.vault_path / 'Logs' / 'linkedin_posts.jsonl'
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def move_to_done(self, filepath: Path):
        """Move processed post to Done folder"""
        self.done.mkdir(parents=True, exist_ok=True)
        dest = self.done / filepath.name
        filepath.rename(dest)
        self.logger.info(f"Moved to Done: {dest.name}")
    
    def check_daily_limit(self) -> bool:
        """Check if daily post limit reached"""
        log_file = self.vault_path / 'Logs' / 'linkedin_posts.jsonl'
        
        if not log_file.exists():
            return True
        
        today = datetime.now().strftime('%Y-%m-%d')
        count = 0
        
        with open(log_file, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if entry['timestamp'].startswith(today) and entry['success']:
                        count += 1
                except:
                    continue
        
        return count < MAX_POSTS_PER_DAY


def main():
    parser = argparse.ArgumentParser(description='LinkedIn Poster for AI Employee')
    parser.add_argument('command', choices=['post', 'draft', 'publish', 'auth', 'status'],
                       help='Command to execute')
    parser.add_argument('--vault', default=None, help='Path to vault')
    parser.add_argument('--topic', default='', help='Post topic')
    parser.add_argument('--type', choices=['milestone', 'insight', 'success', 'update'],
                       default='update', help='Post type')
    
    args = parser.parse_args()

    if args.vault:
        vault_path = Path(args.vault)
    else:
        vault_path = Path(__file__).parent.parent / 'AI_Employee_Vault'

    poster = LinkedInPoster(str(vault_path))
    
    if args.command == 'draft':
        content = poster.generate_post(args.type, args.topic)
        print("Generated LinkedIn Post:")
        print("=" * 50)
        print(content)
        print("=" * 50)
        
        draft_path = poster.create_draft(content, args.topic)
        print(f"\nDraft created: {draft_path}")
        print("Move to /Approved folder when ready to publish")
        
    elif args.command == 'post':
        content = poster.generate_post(args.type, args.topic)
        print("Generated LinkedIn Post:")
        print("=" * 50)
        print(content)
        print("=" * 50)
        
        draft_path = poster.create_draft(content, args.topic)
        print(f"\nDraft created: {draft_path}")
        
        response = input("\nPublish now? (y/n): ").lower().strip()
        if response == 'y':
            if poster.authenticate():
                success = poster.post_to_linkedin(content)
                if success:
                    poster.log_post(draft_path, True)
                    poster.move_to_done(draft_path)
                    print("Post published successfully!")
                else:
                    print("Post publication failed")
        else:
            print("Draft saved for manual approval")
            
    elif args.command == 'publish':
        approved = poster.check_approved_posts()
        
        if not approved:
            print("No approved posts found")
            sys.exit(0)
        
        if not poster.check_daily_limit():
            print(f"Daily post limit reached ({MAX_POSTS_PER_DAY} posts/day)")
            sys.exit(0)
        
        if poster.authenticate():
            for post_file in approved[:1]:
                content = poster.extract_post_content(post_file)
                print(f"Publishing: {post_file.name}")
                
                success = poster.post_to_linkedin(content)
                poster.log_post(post_file, success)
                
                if success:
                    poster.move_to_done(post_file)
                    print("Published successfully!")
                else:
                    print("Publication failed")
        else:
            print("Authentication failed")
            
    elif args.command == 'auth':
        if poster.authenticate():
            print("Authentication successful!")
            print("Session saved for future use")
        else:
            print("Authentication failed")
            sys.exit(1)
            
    elif args.command == 'status':
        print("LinkedIn Poster Status:")
        print(f"  Vault: {vault_path}")
        print(f"  Session Path: {SESSION_PATH}")
        print(f"  Playwright Available: {'Yes' if PLAYWRIGHT_AVAILABLE else 'No'}")
        print(f"  Daily Limit: {MAX_POSTS_PER_DAY} posts/day")
        print(f"  Log File: {LOG_FILE}")


if __name__ == '__main__':
    main()
