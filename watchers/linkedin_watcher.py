"""
LinkedIn Watcher - Silver Tier (Playwright-based)
Monitors LinkedIn messaging for sales/business keywords,
creates .md files in Needs_Action/ with LINKEDIN_ prefix.
"""

import json
import time
from pathlib import Path
from datetime import datetime

from playwright.sync_api import sync_playwright
from base_watcher import BaseWatcher


# -- Config --
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CHECK_INTERVAL = 60  # seconds between scans
SESSION_DIR = Path(__file__).resolve().parent / ".linkedin_session"

PROCESSED_FILE = Path(__file__).resolve().parent / ".linkedin_processed.json"

LOGIN_WAIT_TIMEOUT = 120
PAGE_LOAD_TIMEOUT = 60000
SELECTOR_TIMEOUT = 30000


class LinkedInWatcher(BaseWatcher):
    def __init__(self, vault_path: str, session_path: str):
        super().__init__(vault_path, check_interval=CHECK_INTERVAL)
        self.session_path = Path(session_path)
        self.keywords = ["sales", "client", "project", "business",
                         "invoice", "deal", "partnership", "proposal",
                         "pricing", "budget", "service", "offer"]
        self.processed_ids = self._load_processed()
        self._login_verified = False
        self._playwright = None
        self._browser = None
        self._page = None
        self.logger.info(
            f"LinkedIn Watcher ready ({len(self.processed_ids)} previously processed)"
        )

    def _load_processed(self) -> set:
        if PROCESSED_FILE.exists():
            try:
                return set(json.loads(PROCESSED_FILE.read_text(encoding="utf-8")))
            except (json.JSONDecodeError, Exception):
                return set()
        return set()

    def _save_processed(self):
        PROCESSED_FILE.write_text(
            json.dumps(list(self.processed_ids)), encoding="utf-8",
        )

    def _ensure_browser(self):
        if self._browser and self._page:
            try:
                _ = self._page.url
                return
            except Exception:
                self.logger.info("Browser was closed externally, relaunching...")
                self._browser = None
                self._page = None

        self.logger.info("Launching persistent browser (stays open)...")
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch_persistent_context(
            str(self.session_path),
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
            ],
        )
        self._page = self._browser.pages[0] if self._browser.pages else self._browser.new_page()
        self._page.wait_for_load_state("domcontentloaded")

    def close_browser(self):
        try:
            if self._browser:
                self._browser.close()
            if self._playwright:
                self._playwright.stop()
        except Exception:
            pass
        self._browser = None
        self._page = None
        self._playwright = None

    def _wait_for_login(self, page) -> bool:
        self.logger.info(f"Waiting for LinkedIn login... You have {LOGIN_WAIT_TIMEOUT} seconds.")
        print("\n" + "=" * 58)
        print("  MANUAL LOGIN REQUIRED")
        print("  Please log in to LinkedIn in the browser window.")
        print(f"  Waiting up to {LOGIN_WAIT_TIMEOUT} seconds...")
        print("=" * 58 + "\n")

        elapsed = 0
        poll_interval = 3
        while elapsed < LOGIN_WAIT_TIMEOUT:
            try:
                url = page.url
            except Exception:
                return False

            if any(path in url for path in ["/feed", "/messaging", "/mynetwork", "/in/"]):
                self.logger.info("LinkedIn login detected!")
                self._login_verified = True
                return True

            page.wait_for_timeout(poll_interval * 1000)
            elapsed += poll_interval

        return False

    def _is_logged_in(self, page) -> bool:
        url = page.url
        if any(path in url for path in ["/feed", "/messaging", "/mynetwork", "/in/"]):
            return True
        if "/login" in url or "/signup" in url or "linkedin.com/uas" in url:
            return False
        try:
            nav = page.query_selector("nav.global-nav, header.global-nav")
            return nav is not None
        except Exception:
            return False

    def check_for_updates(self) -> list:
        self._ensure_browser()
        page = self._page

        try:
            page.goto("https://www.linkedin.com/messaging/",
                      wait_until="domcontentloaded",
                      timeout=PAGE_LOAD_TIMEOUT)

            if not self._is_logged_in(page):
                if not self._wait_for_login(page):
                    return []
                page.goto("https://www.linkedin.com/messaging/",
                          wait_until="domcontentloaded",
                          timeout=PAGE_LOAD_TIMEOUT)

            self._login_verified = True

            page.wait_for_selector(
                "ul.msg-conversations-container__conversations-list",
                timeout=SELECTOR_TIMEOUT,
            )

            unread = page.query_selector_all("li.msg-conversation-listitem--unread")

            messages = []
            for chat in unread:
                try:
                    name_el = chat.query_selector("h3.msg-conversation-listitem__participant-names")
                    sender = name_el.inner_text().strip() if name_el else "Unknown"

                    preview_el = chat.query_selector("p.msg-conversation-card__message-snippet")
                    preview = preview_el.inner_text().strip() if preview_el else ""

                    msg_id = f"{sender}_{hash(preview)}"

                    if msg_id in self.processed_ids:
                        continue

                    text_lower = f"{sender} {preview}".lower()
                    matched = [kw for kw in self.keywords if kw in text_lower]

                    if matched:
                        chat.click()
                        page.wait_for_timeout(2000)

                        msg_bubbles = page.query_selector_all("div.msg-s-event-listitem__body")
                        full_text = ""
                        for bubble in msg_bubbles[-5:]:
                            full_text += bubble.inner_text().strip() + "\n"

                        messages.append({
                            "id": msg_id,
                            "sender": sender,
                            "preview": preview,
                            "full_text": full_text.strip() or preview,
                            "keywords": matched,
                        })

                except Exception as e:
                    self.logger.error(f"Error reading chat: {e}")
                    continue

        except Exception as e:
            if "timeout" in str(e).lower() or "selector" in str(e).lower():
                self.logger.warning("LinkedIn page not ready — will retry next cycle.")
            elif "target closed" in str(e).lower() or "closed" in str(e).lower():
                self._browser = None
                self._page = None
            else:
                self.logger.error(f"LinkedIn check error: {e}")
            messages = []

        if not messages:
            self.logger.info("No new keyword-matched LinkedIn messages")

        return messages

    def create_action_file(self, item) -> Path:
        sender = item["sender"]
        preview = item["preview"]
        full_text = item["full_text"]
        keywords = item["keywords"]
        msg_id = item["id"]

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        date_slug = datetime.now().strftime("%Y-%m-%d")

        safe_sender = self._sanitize(sender)
        filename = f"LINKEDIN_{safe_sender}_{date_slug}.md"
        filepath = self.needs_action / filename

        priority = "P3"
        p2_words = ["invoice", "deadline", "proposal", "pricing", "budget"]
        if any(kw in keywords for kw in p2_words):
            priority = "P2"

        content = f"""---
type: linkedin_message
source: linkedin_messaging
sender: "{sender}"
date: "{timestamp}"
priority: {priority}
status: pending
requires_approval: false
keywords_matched: {json.dumps(keywords)}
tags: [linkedin, {', '.join(keywords)}]
summary: "LinkedIn message from {sender} about {', '.join(keywords)}"
---

# LinkedIn Message: {sender}

| Field    | Value |
|----------|-------|
| From     | {sender} |
| Date     | {timestamp} |
| Platform | LinkedIn Messaging |
| Keywords | {', '.join(keywords)} |
| Priority | {priority} |

## Message Preview

{preview}

## Full Conversation (last 5 messages)

{full_text}

## Suggested Actions
- [ ] Review message content
- [ ] Draft LinkedIn post if sales opportunity detected
- [ ] Reply to sender if action needed
- [ ] Archive after processing
"""

        filepath.write_text(content, encoding="utf-8")
        self.processed_ids.add(msg_id)
        self._save_processed()
        self._log_activity(filename, sender, keywords)
        self.logger.info(f'NEW LINKEDIN: "{preview[:50]}..." from {sender}')
        return filepath

    def _sanitize(self, name: str) -> str:
        for ch in ['<', '>', ':', '"', '/', '\\', '|', '?', '*', ' ']:
            name = name.replace(ch, '_')
        return name[:60]

    def _log_activity(self, filename: str, sender: str, keywords: list):
        log_dir = self.vault_path / "Logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "linkedin.log"

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = (
            f"[{timestamp}] DETECTED: {filename} "
            f"| sender={sender} "
            f"| keywords={','.join(keywords)} "
            f"| status=pending\n"
        )
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(entry)

    # ========= LinkedIn Action Methods =========

    def send_message(self, recipient_name: str, message_text: str):
        try:
            self._ensure_browser()
            page = self._page

            page.goto("https://www.linkedin.com/messaging/",
                      wait_until="domcontentloaded",
                      timeout=PAGE_LOAD_TIMEOUT)
            page.wait_for_timeout(2000)

            # Find and click the compose / new message button
            compose_btn = None
            for sel in [
                'button[aria-label="New message"]',
                'button[aria-label="Compose"]',
                'a[href="/messaging/new"]',
                'button:has-text("New")',
            ]:
                compose_btn = page.query_selector(sel)
                if compose_btn:
                    self.logger.info(f"Found compose button via: {sel}")
                    break

            if not compose_btn:
                return {"success": False, "error": "Compose button not found"}

            compose_btn.click()
            page.wait_for_timeout(1500)

            # Find the recipient search input
            search_input = None
            for sel in [
                'input[aria-label="Search for recipients"]',
                'input[placeholder*="name or multiple"]',
                'input[placeholder*="recipient"]',
                'div[role="dialog"] input[type="text"]',
                'input.msg-connections-typeahead__search-field',
            ]:
                search_input = page.query_selector(sel)
                if search_input:
                    self.logger.info(f"Found search input via: {sel}")
                    break

            if not search_input:
                return {"success": False, "error": "Recipient search input not found"}

            # Type recipient name to trigger suggestions
            self.logger.info(f"Searching for recipient: {recipient_name}")
            search_input.click()
            page.wait_for_timeout(300)
            search_input.fill(recipient_name)

            # Wait for the typeahead dropdown to appear
            self.logger.info("Waiting for suggestion dropdown...")
            try:
                page.wait_for_selector(
                    '.msg-connections-typeahead-container li, '
                    '[role="listbox"] li, '
                    '[role="option"]',
                    timeout=5000
                )
                page.wait_for_timeout(500)  # Let all results render
            except Exception:
                self.logger.warning("Dropdown selector timed out, continuing anyway...")
                page.wait_for_timeout(2000)

            # Log what suggestions appeared
            suggestions = page.evaluate('''() => {
                const items = Array.from(document.querySelectorAll(
                    ".msg-connections-typeahead-container li, [role=listbox] li, [role=option]"
                ));
                return items.map(el => el.innerText.trim().slice(0, 80));
            }''')
            self.logger.info(f"Suggestions found: {suggestions}")

            # --- Smart recipient selection ---
            # Find best match index: prefer 1st connection > 2nd > 3rd+
            target_index = page.evaluate(
                """(function(name) {
                    var items = Array.from(document.querySelectorAll(
                        ".msg-connections-typeahead-container li, [role=listbox] li, [role=option]"
                    ));
                    if (items.length === 0) return 0;
                    var nameLower = name.toLowerCase();
                    var firstName = nameLower.split(" ")[0];
                    var bestIdx = 0;
                    var bestScore = -1;
                    for (var i = 0; i < items.length; i++) {
                        var text = items[i].innerText.toLowerCase();
                        if (text.indexOf(firstName) === -1) continue;
                        var score = 0;
                        if (text.indexOf(nameLower) !== -1) score += 10;
                        if (text.indexOf("1st") !== -1) score += 20;
                        else if (text.indexOf("2nd") !== -1) score += 5;
                        if (text.indexOf("online") !== -1 || text.indexOf("reachable") !== -1) score += 2;
                        if (score > bestScore) { bestScore = score; bestIdx = i; }
                    }
                    return bestIdx;
                })""",
                recipient_name
            )
            self.logger.info(f"Best match at suggestion index: {target_index}")

            # Get the target suggestion text so we know what to look for
            best_text = page.evaluate(
                """(function(idx) {
                    var items = Array.from(document.querySelectorAll(
                        ".msg-connections-typeahead-container li, [role=listbox] li, [role=option]"
                    ));
                    return items[idx] ? items[idx].innerText.trim().slice(0, 80) : "";
                })""",
                target_index
            )
            self.logger.info(f"Target suggestion text: {best_text!r}")

            # Press ArrowDown until the highlighted item matches our target.
            # We check by name + connection degree to avoid wrong person.
            target_name_lower = recipient_name.lower().split()[0]
            target_is_first = "1st" in best_text
            found = False
            for attempt in range(12):
                search_input.press("ArrowDown")
                page.wait_for_timeout(250)
                highlighted = page.evaluate(
                    "(function() {"
                    "  var a = document.querySelector('[aria-selected=true]');"
                    "  return a ? a.innerText.trim().slice(0, 80) : '';"
                    "})()"
                )
                self.logger.info(f"ArrowDown {attempt+1}: {highlighted[:60]!r}")
                if target_name_lower in highlighted.lower():
                    highlighted_is_first = "1st" in highlighted
                    if target_is_first and highlighted_is_first:
                        found = True
                        break
                    elif not target_is_first and not highlighted_is_first:
                        found = True
                        break

            if not found:
                self.logger.warning("Exact match not found — using current highlighted item")

            # Confirm selection
            search_input.press("Enter")
            page.wait_for_timeout(1500)

            # Log the search input value — it clears when a chip/token is added
            inp_value = page.evaluate(
                "(function() {"
                "  var inp = document.querySelector('.msg-connections-typeahead__search-field')"
                "  || document.querySelector('input[placeholder]');"
                "  return inp ? inp.value : 'cleared';"
                "})()"
            )
            self.logger.info(f"Search input value after selection: {inp_value!r}")

            # Wait for compose panel to load after recipient is selected
            self.logger.info("Waiting for message compose panel to load...")
            page.wait_for_timeout(2500)

            # Find message input — poll up to 10 seconds
            message_input = None
            for wait_attempt in range(10):
                for sel in [
                    "div.msg-form__contenteditable",
                    'div[contenteditable="true"][role="textbox"]',
                    'div[contenteditable="true"]',
                ]:
                    message_input = page.query_selector(sel)
                    if message_input:
                        self.logger.info(f"Found message input via: {sel}")
                        break
                if message_input:
                    break
                self.logger.info(f"Message input not ready (attempt {wait_attempt+1}/10)...")
                page.wait_for_timeout(1000)

            if not message_input:
                return {"success": False, "error": "Message input not found"}

            message_input.click()
            page.wait_for_timeout(300)

            # Use keyboard.insert_text for Unicode support
            page.keyboard.insert_text(message_text)
            page.wait_for_timeout(500)

            # Click send
            send_btn = None
            for sel in [
                'button.msg-form__send-button',
                'button[aria-label*="Send"]',
                'button:has-text("Send")',
            ]:
                send_btn = page.query_selector(sel)
                if send_btn:
                    break

            if not send_btn:
                return {"success": False, "error": "Send button not found"}

            send_btn.click()
            page.wait_for_timeout(1500)
            self.logger.info(f"Message sent to {recipient_name}")
            return {"success": True, "recipient": recipient_name}

        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
            return {"success": False, "error": str(e)}

    def create_post(self, post_text: str, image_path: str = None):
        try:
            self._ensure_browser()
            page = self._page

            page.goto("https://www.linkedin.com/feed/",
                      wait_until="domcontentloaded",
                      timeout=PAGE_LOAD_TIMEOUT)
            page.wait_for_timeout(3000)

            # Click Start a Post
            post_trigger = page.query_selector('button[aria-label="Start a post"]')
            if not post_trigger:
                post_trigger = page.query_selector('div.share-box-feed-entry__trigger button')
            if not post_trigger:
                post_trigger = page.query_selector('button:has-text("Start a post")')

            if post_trigger:
                post_trigger.click()
                page.wait_for_timeout(2000)
            else:
                self.logger.warning("Post trigger not found, trying direct URL")
                page.goto("https://www.linkedin.com/feed/detail/draft/",
                          wait_until="domcontentloaded",
                          timeout=PAGE_LOAD_TIMEOUT)
                page.wait_for_timeout(2000)

            # Find text area
            text_area = page.query_selector('div[contenteditable="true"][role="textbox"]')
            if not text_area:
                editables = page.query_selector_all('div[contenteditable="true"]')
                if editables:
                    text_area = editables[-1]
            if not text_area:
                text_area = page.query_selector('div[placeholder*="What do you want to share?"]')
            if not text_area:
                dialog = page.query_selector('div[role="dialog"]')
                if dialog:
                    text_area = dialog.query_selector('div[contenteditable="true"]')

            if text_area:
                text_area.click()
                page.wait_for_timeout(1000)

                # Select all existing content and delete it first
                text_area.press('Control+a')
                page.wait_for_timeout(100)
                text_area.press('Delete')
                page.wait_for_timeout(100)

                # Use keyboard.insert_text() — Playwright's dedicated method for
                # inserting Unicode text. Unlike type(), it doesn't simulate
                # individual keypresses, so ━━━, ✓, ✗, •, →, emojis all work.
                self.logger.info(f"Inserting post text ({len(post_text)} chars) via keyboard.insert_text...")
                page.keyboard.insert_text(post_text)
                page.wait_for_timeout(1000)

                # Verify content was inserted
                inserted = page.evaluate('''() => {
                    const selectors = [
                        'div[contenteditable="true"][role="textbox"]',
                        'div[contenteditable="true"]'
                    ];
                    for (const sel of selectors) {
                        const el = document.querySelector(sel);
                        if (el && el.innerText.length > 0) return el.innerText.length;
                    }
                    return 0;
                }''')
                self.logger.info(f"Text area char count after insert: {inserted}")

                if inserted == 0:
                    # Fallback: set innerHTML via JS and fire React input events
                    self.logger.warning("insert_text produced no content — using JS innerHTML fallback")
                    page.evaluate('''(text) => {
                        const el = document.querySelector(
                            'div[contenteditable="true"][role="textbox"]'
                        ) || document.querySelector('div[contenteditable="true"]');
                        if (!el) return;
                        el.focus();
                        // Use execCommand so browser treats it as user input
                        document.execCommand("selectAll", false, null);
                        document.execCommand("insertText", false, text);
                        // Fire events so LinkedIn/React registers the change
                        el.dispatchEvent(new Event("input", {bubbles: true}));
                        el.dispatchEvent(new Event("change", {bubbles: true}));
                    }''', post_text)
                    page.wait_for_timeout(1000)

                page.wait_for_timeout(500)

                # Attach image if provided
                if image_path:
                    media_btn = page.query_selector('button[aria-label*="Add media"]')
                    if not media_btn:
                        media_btn = page.query_selector('button:has-text("Media")')
                    if not media_btn:
                        media_btn = page.query_selector('button:has-text("Image")')
                    if media_btn:
                        media_btn.click()
                        page.wait_for_timeout(500)
                        file_input = page.query_selector('input[type="file"]')
                        if file_input:
                            file_input.set_input_files(image_path)
                            page.wait_for_timeout(2000)

                # Click the main Post button
                post_btn = page.query_selector('button[aria-label*="Post"]')
                if not post_btn:
                    post_btn = page.query_selector('button.share-actions__primary-btn')
                if not post_btn:
                    post_btn = page.query_selector('button:has-text("Post")')

                if not post_btn:
                    return {"success": False, "error": "Post button not found"}

                is_disabled = post_btn.is_disabled()
                if is_disabled:
                    self.logger.warning("Post button disabled, force clicking")
                    post_btn.click(force=True)
                else:
                    post_btn.click()

                page.wait_for_timeout(3000)

                # -------------------------------------------------------
                # Handle the "Who can see your post?" visibility dialog
                # -------------------------------------------------------
                self.logger.info("Checking for post visibility dialog...")

                try:
                    page.wait_for_selector('div[role="dialog"]', timeout=8000)
                    page.wait_for_timeout(1000)  # Extra wait for React to fully hydrate
                except Exception:
                    # No dialog appeared — post submitted directly, we're done
                    self.logger.info("No visibility dialog — post submitted directly")
                    return {"success": True, "post_text": post_text[:50] + "..."}

                dialog = page.query_selector('div[role="dialog"]')
                if not dialog:
                    self.logger.info("Dialog gone already — post submitted")
                    return {"success": True, "post_text": post_text[:50] + "..."}

                self.logger.info("Visibility dialog present — selecting 'Anyone' via JS...")

                # --- Select "Anyone" radio using JavaScript (most reliable) ---
                # JS approach bypasses pointer-events issues and triggers React synthetic events
                selected = page.evaluate('''() => {
                    // Strategy 1: radio with EVERYONE/anyone in value or id
                    const radios = Array.from(document.querySelectorAll('input[type="radio"]'));
                    let target = radios.find(r =>
                        (r.value && (r.value.includes('EVERYONE') || r.value.toLowerCase().includes('anyone'))) ||
                        (r.id && (r.id.includes('EVERYONE') || r.id.toLowerCase().includes('anyone')))
                    );
                    // Strategy 2: first radio in the dialog (topmost = Anyone/Public)
                    if (!target) {
                        const dialog = document.querySelector('div[role="dialog"]');
                        if (dialog) {
                            target = dialog.querySelector('input[type="radio"]');
                        }
                    }
                    if (target) {
                        // Simulate full React event sequence
                        target.focus();
                        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                            window.HTMLInputElement.prototype, 'checked'
                        ).set;
                        nativeInputValueSetter.call(target, true);
                        target.dispatchEvent(new MouseEvent('mousedown', {bubbles: true}));
                        target.dispatchEvent(new MouseEvent('mouseup', {bubbles: true}));
                        target.dispatchEvent(new MouseEvent('click', {bubbles: true}));
                        target.dispatchEvent(new Event('change', {bubbles: true}));
                        return true;
                    }
                    return false;
                }''')

                self.logger.info(f"Radio selection via JS: {'success' if selected else 'not found, trying fallback'}")
                page.wait_for_timeout(1000)

                if not selected:
                    # Fallback: click the li containing "Anyone"
                    for sel in [
                        'div[role="dialog"] li:has-text("Anyone")',
                        'div[role="dialog"] label:has-text("Anyone")',
                    ]:
                        el = page.query_selector(sel)
                        if el:
                            el.click()
                            page.wait_for_timeout(1000)
                            self.logger.info(f"Fallback click on: {sel}")
                            break

                # --- Wait for Done button and click it ---
                self.logger.info("Waiting for Done button to enable...")
                done_clicked = False

                for attempt in range(30):  # up to 15 seconds
                    # Re-trigger radio every 5 attempts in case state didn't register
                    if attempt > 0 and attempt % 5 == 0:
                        page.evaluate('''() => {
                            const dialog = document.querySelector('div[role="dialog"]');
                            if (!dialog) return;
                            const radio = dialog.querySelector('input[type="radio"]');
                            if (radio) {
                                radio.dispatchEvent(new MouseEvent('click', {bubbles: true}));
                                radio.dispatchEvent(new Event('change', {bubbles: true}));
                            }
                        }''')
                        page.wait_for_timeout(300)

                    # Find Done button — check multiple selectors
                    done_btn = None
                    for done_sel in [
                        'div[role="dialog"] button:has-text("Done")',
                        'button[aria-label*="Done"]',
                        'button:has-text("Done")',
                    ]:
                        candidate = page.query_selector(done_sel)
                        if candidate:
                            done_btn = candidate
                            break

                    if done_btn:
                        # Check enabled state via attribute (more reliable than .is_disabled())
                        disabled_attr = done_btn.get_attribute("disabled")
                        aria_disabled = done_btn.get_attribute("aria-disabled")

                        if disabled_attr is None and aria_disabled != "true":
                            done_btn.click()
                            page.wait_for_timeout(2000)
                            self.logger.info(f"Done clicked! (attempt {attempt + 1})")
                            done_clicked = True
                            break
                        else:
                            self.logger.info(f"Attempt {attempt + 1}: Done still disabled "
                                             f"(disabled={disabled_attr}, aria-disabled={aria_disabled})")
                    else:
                        self.logger.info(f"Attempt {attempt + 1}: Done button not found in DOM yet")

                    page.wait_for_timeout(500)

                if not done_clicked:
                    # Nuclear option: remove disabled attr and force click via JS
                    self.logger.warning("Done button never enabled naturally — forcing via JS")
                    forced = page.evaluate('''() => {
                        const btns = Array.from(document.querySelectorAll('button'));
                        const done = btns.find(b => b.textContent.trim() === 'Done');
                        if (done) {
                            done.removeAttribute('disabled');
                            done.setAttribute('aria-disabled', 'false');
                            done.click();
                            return true;
                        }
                        return false;
                    }''')
                    page.wait_for_timeout(2000)
                    if forced:
                        self.logger.info("Force-clicked Done via JS DOM manipulation")
                        done_clicked = True
                    else:
                        self.logger.error("Could not find Done button at all — post may not have published")
                        return {"success": False, "error": "Done button not clickable"}

                # -------------------------------------------------------
                # STEP 2: After Done, LinkedIn returns to the composer.
                # We must click the composer's own "Post" button to publish.
                # Key insight: scope the search to the composer modal ONLY
                # to avoid clicking wrong buttons elsewhere on the feed.
                # -------------------------------------------------------
                self.logger.info("Done clicked — waiting for visibility dialog to close...")
                page.wait_for_timeout(1500)

                # Wait for the visibility dialog to fully detach
                try:
                    page.wait_for_selector('div[role="dialog"]', state="detached", timeout=6000)
                    self.logger.info("Visibility dialog closed")
                except Exception:
                    self.logger.info("Visibility dialog may still be present or already gone")
                page.wait_for_timeout(1000)

                # Take a debug screenshot so we can see what's on screen
                try:
                    page.screenshot(path='debug_after_done.png')
                    self.logger.info("Screenshot saved: debug_after_done.png")
                except Exception:
                    pass

                # Log all buttons visible right now for debugging
                btn_info = page.evaluate('''() => {
                    const btns = Array.from(document.querySelectorAll('button'));
                    return btns.map(b => ({
                        text: b.textContent.trim().slice(0, 40),
                        disabled: b.disabled,
                        ariaDisabled: b.getAttribute("aria-disabled"),
                        ariaLabel: b.getAttribute("aria-label"),
                        className: b.className.slice(0, 60)
                    })).filter(b => b.text.length > 0);
                }''')
                self.logger.info(f"Buttons on page after Done: {btn_info}")

                self.logger.info("Searching for final Post button inside composer...")

                # Poll for the enabled Post button scoped to the share/composer area
                final_clicked = False
                for attempt in range(20):  # up to 10 seconds
                    result = page.evaluate('''() => {
                        // Look for Post button ONLY inside the composer/share modal
                        // Composer is typically: .share-box, .share-creation-state,
                        //   div[data-test-modal], or the outermost share container
                        const composerSelectors = [
                            '.share-creation-state',
                            '.share-box-feed-entry__modal',
                            'div[data-test-modal]',
                            '.share-box',
                            '.editor-container',
                        ];

                        let container = null;
                        for (const sel of composerSelectors) {
                            container = document.querySelector(sel);
                            if (container) break;
                        }

                        // Search scoped to composer, or fall back to full page
                        const scope = container || document;
                        const btns = Array.from(scope.querySelectorAll('button'));

                        // Find a Post button that is enabled
                        const postBtn = btns.find(b => {
                            const text = b.textContent.trim();
                            const label = b.getAttribute("aria-label") || "";
                            const isPost = text === "Post" || label.includes("Post");
                            const enabled = !b.disabled && b.getAttribute("aria-disabled") !== "true";
                            return isPost && enabled;
                        });

                        if (postBtn) {
                            postBtn.click();
                            return {
                                clicked: true,
                                text: postBtn.textContent.trim(),
                                label: postBtn.getAttribute("aria-label"),
                                inComposer: container !== null
                            };
                        }
                        return {clicked: false};
                    }''')

                    self.logger.info(f"Final Post attempt {attempt + 1}: {result}")

                    if result.get("clicked"):
                        self.logger.info(
                            f"Final Post clicked! text='{result.get('text')}' "
                            f"label='{result.get('label')}' "
                            f"inComposer={result.get('inComposer')}"
                        )
                        final_clicked = True
                        break

                    page.wait_for_timeout(500)

                if not final_clicked:
                    self.logger.error("Could not find an enabled Post button after Done")
                    try:
                        page.screenshot(path='debug_no_post_btn.png')
                    except Exception:
                        pass
                    return {"success": False, "error": "Final Post button not found after visibility dialog"}

                # Wait and verify the composer closed (= post was accepted by LinkedIn)
                page.wait_for_timeout(2000)
                try:
                    page.wait_for_selector(
                        '.share-creation-state, .share-box-feed-entry__modal, div[data-test-modal]',
                        state="detached",
                        timeout=8000
                    )
                    self.logger.info("Composer closed — post successfully published!")
                except Exception:
                    # Composer didn't close — LinkedIn may have shown an error
                    self.logger.warning(
                        "Composer did not close after Post click — post may not have published. "
                        "Check debug_post_final.png"
                    )
                    try:
                        page.screenshot(path='debug_post_final.png')
                    except Exception:
                        pass

                try:
                    page.screenshot(path='debug_post_done.png')
                    self.logger.info("Screenshot saved: debug_post_done.png")
                except Exception:
                    pass

                self.logger.info("LinkedIn post created successfully")
                return {"success": True, "post_text": post_text[:50] + "..."}

            else:
                self.logger.error("Could not find post text area")
                return {"success": False, "error": "Post text area not found"}

        except Exception as e:
            self.logger.error(f"Failed to create post: {e}")
            return {"success": False, "error": str(e)}

    def reply_to_message(self, message_text: str):
        try:
            self._ensure_browser()
            page = self._page

            message_input = page.query_selector('div.msg-form__contenteditable')
            if message_input:
                message_input.click()
                message_input.fill(message_text)
                page.wait_for_timeout(500)

                send_btn = page.query_selector('button.msg-form__send-button')
                if send_btn:
                    send_btn.click()
                    page.wait_for_timeout(1000)
                    return {"success": True}
                else:
                    return {"success": False, "error": "Send button not found"}
            else:
                return {"success": False, "error": "Message input not found"}

        except Exception as e:
            self.logger.error(f"Failed to send reply: {e}")
            return {"success": False, "error": str(e)}


def main():
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    vault_path = PROJECT_ROOT / "AI_Employee_Vault"

    print("=" * 58)
    print("  LINKEDIN WATCHER - Silver Tier (Playwright)")
    print(f"  Checking every {CHECK_INTERVAL} seconds")
    print(f"  Session:  {SESSION_DIR}")
    print(f"  Output:   {vault_path / 'Needs_Action'}")
    print("=" * 58)

    watcher = LinkedInWatcher(str(vault_path), str(SESSION_DIR))
    try:
        watcher.run()
    except KeyboardInterrupt:
        print("\n  Shutting down LinkedIn Watcher...")
    finally:
        watcher.close_browser()
        print("  Browser closed. Goodbye!")


if __name__ == "__main__":
    main()