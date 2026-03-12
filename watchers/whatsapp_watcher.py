#!/usr/bin/env python3
"""
WhatsApp Watcher — 2026 compatible (FIXED send/search)
"""
import sys
import json
import time
import logging
import hashlib
import base64
from pathlib import Path
from datetime import datetime
import argparse

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

SESSION_DIR = Path(__file__).resolve().parent / '.whatsapp_session'
CHECK_INTERVAL = 30
VAULT_PATH_DEFAULT = Path(__file__).resolve().parent.parent / 'AI_Employee_Vault_Gold_Tier'
LOG_FILE = VAULT_PATH_DEFAULT / 'Logs' / 'whatsapp_watcher.log'
MEDIA_DIR_NAME = 'WhatsApp_Media'
AUTH_TIMEOUT = 300000


class WhatsAppWatcher:

    def __init__(self, vault_path=None, check_interval=CHECK_INTERVAL):
        self.vault_path = Path(vault_path or VAULT_PATH_DEFAULT)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.media_dir = self.vault_path / MEDIA_DIR_NAME
        self.check_interval = check_interval
        
        # Save processed files in config folder
        self.project_root = Path(__file__).resolve().parent.parent
        self.config_dir = self.project_root / 'config'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.processed_ids_file = self.config_dir / 'processed_messages.json'
        
        self.running = False
        self.browser = None
        self.page = None
        self.playwright = None

        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

        # Fix Windows cp1252 crash - force UTF-8 everywhere
        file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
        try:
            stream_handler = logging.StreamHandler(
                open(sys.stdout.fileno(), mode='w', encoding='utf-8', closefd=False)
            )
        except Exception:
            stream_handler = logging.StreamHandler()

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[file_handler, stream_handler]
        )
        self.logger = logging.getLogger('WhatsAppWatcher')
        self.processed_messages = self._load_processed_messages()
        self.priority_keywords = [
            'urgent', 'asap', 'immediate', 'quick', 'invoice', 'payment',
            'money', 'billing', 'client', 'project', 'meeting', 'deadline',
            'help', 'issue', 'problem', 'error', 'call', 'today'
        ]
        if not PLAYWRIGHT_AVAILABLE:
            self.logger.error("Playwright not installed")
        self.logger.info(f"Session: {SESSION_DIR}")
        self.logger.info(f"Vault: {self.vault_path}")

    # === Persistence ===
    def _load_processed_messages(self):
        if self.processed_ids_file.exists():
            try:
                with open(self.processed_ids_file, 'r') as f:
                    return set(json.load(f))
            except Exception:
                return set()
        return set()

    def _save_processed_messages(self):
        with open(self.processed_ids_file, 'w') as f:
            json.dump(list(self.processed_messages)[-1000:], f)

    def _message_hash(self, chat, text):
        return hashlib.md5(f"{chat}:{text}".encode()).hexdigest()

    # === Browser ===
    def _launch_browser(self):
        if self.browser:
            return
        self.playwright = sync_playwright().start()
        SESSION_DIR.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Launching browser: {SESSION_DIR}")
        self.browser = self.playwright.chromium.launch_persistent_context(
            str(SESSION_DIR),
            headless=False,
            args=['--disable-blink-features=AutomationControlled'],
            viewport={'width': 1280, 'height': 800}
        )
        self.page = (
            self.browser.pages[0] if self.browser.pages
            else self.browser.new_page()
        )

    def _close_browser(self):
        try:
            if self.browser:
                self.browser.close()
        except Exception:
            pass
        try:
            if self.playwright:
                self.playwright.stop()
        except Exception:
            pass
        self.browser = None
        self.page = None
        self.playwright = None

    def _is_logged_in(self):
        try:
            self.page.wait_for_timeout(2000)
            for sel in ['#pane-side', '[data-testid="chat-list"]']:
                if self.page.query_selector(sel):
                    return True
            return (
                "web.whatsapp.com" in self.page.url
                and "WhatsApp" in (self.page.title() or "")
            )
        except Exception:
            return False

    # === Debug ===
    def _screenshot(self, name="debug"):
        try:
            self.page.screenshot(path=f"{name}.png")
            self.logger.info(f"Screenshot: {name}.png")
        except Exception:
            pass

    def _dom_state(self, label=""):
        try:
            info = self.page.evaluate('''() => {
                const eds = document.querySelectorAll('[contenteditable="true"]');
                return {
                    editables: Array.from(eds).map(el => ({
                        dataTab: el.getAttribute('data-tab'),
                        testid: el.getAttribute('data-testid'),
                        visible: el.offsetHeight > 0,
                        inFooter: !!el.closest('footer'),
                        inMain: !!el.closest('#main'),
                    })),
                    hasMain: !!document.querySelector('#main'),
                    hasFooter: !!document.querySelector('footer'),
                    hasPaneSide: !!document.querySelector('#pane-side'),
                };
            }''')
            self.logger.info(f"DOM [{label}]: {json.dumps(info, indent=2)}")
            return info
        except Exception as e:
            self.logger.debug(f"DOM dump failed: {e}")
            return {}

    # === Auth ===
    def authenticate(self):
        if not PLAYWRIGHT_AVAILABLE:
            return False
        try:
            self._launch_browser()
            self.page.goto(
                'https://web.whatsapp.com',
                wait_until='domcontentloaded', timeout=60000
            )
            if self._is_logged_in():
                self.logger.info("Already logged in")
                return True
            print("\n" + "=" * 60)
            print("SCAN QR CODE with your phone")
            print("Settings > Linked Devices > Link a Device")
            print("Waiting up to 5 minutes...")
            print("=" * 60 + "\n")
            start = time.time()
            while time.time() - start < (AUTH_TIMEOUT / 1000):
                if self._is_logged_in():
                    print("\n[OK] Authenticated!\n")
                    self.logger.info("Authenticated")
                    return True
                time.sleep(2)
            self.logger.error("Auth timeout")
            return False
        except Exception as e:
            self.logger.error(f"Auth error: {e}")
            return False

    def ensure_authenticated(self):
        if not self.browser or not self.page:
            if not self.authenticate():
                raise RuntimeError("Auth failed")
        try:
            current = self.page.url
        except Exception:
            self.browser = None
            self.page = None
            if not self.authenticate():
                raise RuntimeError("Auth failed after crash")
            return True
        if "web.whatsapp.com" not in current:
            self.page.goto(
                'https://web.whatsapp.com',
                wait_until='domcontentloaded', timeout=60000
            )
        if not self._is_logged_in():
            self.page.wait_for_timeout(5000)
            if not self._is_logged_in():
                raise RuntimeError("Session expired")
        return True

    def _wait_ready(self, timeout=15000):
        for sel in ['#pane-side', '[data-testid="chat-list"]']:
            try:
                self.page.wait_for_selector(
                    sel, timeout=timeout, state="visible"
                )
                self.logger.info(f"WhatsApp ready ({sel})")
                return True
            except Exception:
                continue
        return False

    # ======================================================
    #  WAIT FOR CHAT TO FULLY LOAD (footer + message input)
    # ======================================================
    def _wait_for_chat_ready(self, timeout_seconds=20):
        """
        Wait until footer AND message input exist.
        Returns True if chat is fully ready.
        """
        self.logger.info(f"Waiting for chat to fully load (up to {timeout_seconds}s)...")

        for i in range(timeout_seconds):
            has_footer = self.page.query_selector('footer')
            has_main = self.page.query_selector('#main')

            if has_footer and has_main:
                # Double-check: is there a contenteditable in footer?
                has_input = self.page.evaluate('''() => {
                    const f = document.querySelector('footer');
                    if (!f) return false;
                    const inp = f.querySelector('[contenteditable="true"]');
                    return !!(inp && inp.offsetHeight > 0);
                }''')

                if has_input:
                    self.logger.info(
                        f"Chat fully ready: #main + footer + input "
                        f"(took {i+1}s)"
                    )
                    return True
                elif i > 5:
                    # footer exists but no input after 5s - good enough
                    self.logger.info(
                        f"Chat has #main + footer but input not yet "
                        f"visible (took {i+1}s) - proceeding"
                    )
                    return True

            if i % 3 == 0 and i > 0:
                self.logger.info(
                    f"  still waiting... main={bool(has_main)} "
                    f"footer={bool(has_footer)} ({i}s)"
                )

            self.page.wait_for_timeout(1000)

        self.logger.error(f"Chat not ready after {timeout_seconds}s")
        self._screenshot("debug_chat_not_ready")
        self._dom_state("chat_not_ready")
        return False

    # ======================================================
    #  SEARCH AND OPEN CHAT - FIXED WITH MOUSE.CLICK
    # ======================================================
    def search_chat(self, contact_name: str) -> bool:
        """
        Search for a contact and open its chat.

        Uses page.mouse.click(x, y) on the search result's
        exact screen coordinates. This triggers real browser
        mousedown/mouseup/click events that React responds to.

        NO Escape key is pressed after opening.
        """
        try:
            self.page.wait_for_timeout(1000)

            # ── Step 1: Find search box ──
            search_box = None
            for sel in [
                'div[contenteditable="true"][data-tab="3"]',
                '[data-testid="chat-list-search"]',
            ]:
                try:
                    el = self.page.wait_for_selector(
                        sel, timeout=5000, state="visible"
                    )
                    if el:
                        search_box = el
                        self.logger.info(f"Search box: {sel}")
                        break
                except Exception:
                    continue

            if not search_box:
                self.logger.error("Search box not found")
                self._screenshot("debug_no_searchbox")
                return False

            # ── Step 2: Clear and type contact name ──
            search_box.click()
            self.page.wait_for_timeout(300)
            self.page.keyboard.press("Control+A")
            self.page.keyboard.press("Backspace")
            self.page.wait_for_timeout(300)
            search_box.type(contact_name, delay=80)
            self.logger.info(f"Typed: '{contact_name}'")

            # Wait for search results to render
            self.page.wait_for_timeout(3000)
            self._screenshot("debug_search_results")

            # ── Step 3: Find matching contact in results ──
            target = contact_name.lower().strip()
            spans = self.page.query_selector_all('span[title]')
            self.logger.info(f"Found {len(spans)} span[title] elements")

            matching_span = None
            for span in spans:
                title = (span.get_attribute('title') or '').strip()
                if not title:
                    continue
                if (title.lower() == target
                        or target in title.lower()
                        or title.lower() in target):
                    self.logger.info(f"Match found: '{title}'")
                    matching_span = span
                    break

            if not matching_span:
                self.logger.error(f"No matching contact for '{contact_name}'")
                self._screenshot("debug_no_match")
                return False

            # ── Step 4: Click using MOUSE COORDINATES ──
            # This is the key fix. page.mouse.click sends real
            # mousedown/mouseup/click at exact screen position.
            # React event handlers WILL fire.

            chat_opened = False

            # Method A: Mouse click on the span's bounding box
            self.logger.info("Method A: mouse.click on bounding box...")
            box = matching_span.bounding_box()
            if box and box['width'] > 0 and box['height'] > 0:
                cx = box['x'] + box['width'] / 2
                cy = box['y'] + box['height'] / 2
                self.logger.info(f"  Clicking at ({cx:.0f}, {cy:.0f})")

                self.page.mouse.click(cx, cy)
                self.page.wait_for_timeout(1000)

                # Check if chat opened
                if self._wait_for_chat_ready(timeout_seconds=15):
                    chat_opened = True
                    self.logger.info("  [OK] Chat opened via mouse click!")
            else:
                self.logger.info("  Bounding box not available")

            # Method B: Click a bit higher (on the row, not just name)
            if not chat_opened and box:
                self.logger.info("Method B: clicking row area...")
                # Click 50px to the left and centered vertically
                # This hits the chat row area, not just the name text
                rx = box['x'] - 50 if box['x'] > 60 else box['x']
                ry = box['y'] + box['height'] / 2
                self.page.mouse.click(rx, ry)
                self.page.wait_for_timeout(1000)
                if self._wait_for_chat_ready(timeout_seconds=10):
                    chat_opened = True
                    self.logger.info("  [OK] Chat opened via row click!")

            # Method C: Keyboard navigation
            if not chat_opened:
                self.logger.info("Method C: keyboard ArrowDown + Enter...")
                # Re-focus search box
                search_box.click()
                self.page.wait_for_timeout(300)
                self.page.keyboard.press("ArrowDown")
                self.page.wait_for_timeout(300)
                self.page.keyboard.press("Enter")
                self.page.wait_for_timeout(1000)
                if self._wait_for_chat_ready(timeout_seconds=15):
                    chat_opened = True
                    self.logger.info("  [OK] Chat opened via keyboard!")

            # Method D: Playwright locator API
            if not chat_opened:
                self.logger.info("Method D: Playwright locator...")
                try:
                    loc = self.page.locator(
                        f'span[title="{contact_name}"]'
                    ).first
                    loc.click(timeout=5000)
                    self.page.wait_for_timeout(1000)
                    if self._wait_for_chat_ready(timeout_seconds=10):
                        chat_opened = True
                        self.logger.info("  [OK] Chat opened via locator!")
                except Exception as e:
                    self.logger.info(f"  Locator failed: {e}")

            if not chat_opened:
                self.logger.error("ALL 4 methods failed to open chat")
                self._screenshot("debug_all_methods_failed")
                self._dom_state("all_methods_failed")
                return False

            # ── Step 5: NO ESCAPE KEY ──
            # Previous bug: Escape was CLOSING the chat
            # The chat is already open, search auto-dismisses
            # DO NOTHING HERE

            self.logger.info(
                f"Chat '{contact_name}' opened successfully"
            )
            return True

        except Exception as e:
            self.logger.error(f"search_chat error: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False

    # ======================================================
    #  FIND MESSAGE INPUT (not search box)
    # ======================================================
    def _find_message_input(self, retries=5):
        """
        Find the message compose box.
        Search box = data-tab='3' (SKIP THIS)
        Message box = data-tab='10' or inside <footer>
        """
        for attempt in range(1, retries + 1):
            self.logger.info(
                f"Finding message input ({attempt}/{retries})..."
            )

            if attempt == 1:
                self._dom_state("find_input")

            # P1: Exact WhatsApp selectors
            for sel in [
                '[data-testid="conversation-compose-box-input"]',
                'div[data-tab="10"][contenteditable="true"]',
                'div[data-tab="10"]',
            ]:
                el = self.page.query_selector(sel)
                if el:
                    try:
                        if el.is_visible():
                            self.logger.info(f"Input found: {sel}")
                            return el
                    except Exception:
                        pass

            # P2: Inside footer
            footer = self.page.query_selector('footer')
            if footer:
                for sub in [
                    'div[contenteditable="true"]',
                    '[role="textbox"]',
                ]:
                    el = footer.query_selector(sub)
                    if el:
                        try:
                            if el.is_visible():
                                self.logger.info(
                                    f"Input found: footer > {sub}"
                                )
                                return el
                        except Exception:
                            pass

            # P3: Inside #main, skip data-tab="3"
            main = self.page.query_selector('#main')
            if main:
                for c in main.query_selector_all(
                    '[contenteditable="true"]'
                ):
                    tab = c.get_attribute("data-tab") or ""
                    if tab == "3":
                        continue
                    try:
                        if c.is_visible():
                            self.logger.info(
                                "Input found: #main contenteditable"
                            )
                            return c
                    except Exception:
                        continue

            # P4: JavaScript deep search
            try:
                handle = self.page.evaluate_handle('''() => {
                    const f = document.querySelector('footer');
                    if (f) {
                        const i = f.querySelector(
                            '[contenteditable="true"]'
                        );
                        if (i && i.offsetHeight > 0) return i;
                    }
                    const d = document.querySelector(
                        'div[data-tab="10"]'
                    );
                    if (d && d.offsetHeight > 0) return d;
                    const m = document.querySelector('#main');
                    if (m) {
                        for (const e of m.querySelectorAll(
                            '[contenteditable="true"]'
                        )) {
                            if (e.getAttribute('data-tab') !== '3'
                                && e.offsetHeight > 0) return e;
                        }
                    }
                    return null;
                }''')
                el = handle.as_element()
                if el:
                    self.logger.info("Input found: JS fallback")
                    return el
            except Exception:
                pass

            # Click #main to trigger lazy rendering
            try:
                m = self.page.query_selector('#main')
                if m:
                    m.click()
            except Exception:
                pass
            self.page.wait_for_timeout(2000)

        self._screenshot("debug_no_msg_input")
        self._dom_state("input_not_found")
        self.logger.error("Message input NOT found")
        return None

    # ======================================================
    #  SEND MESSAGE
    # ======================================================
    def send_message(self, contact_name: str, message_text: str) -> dict:
        try:
            self.ensure_authenticated()
            self._wait_ready()

            self.logger.info(f"Opening chat: {contact_name}")
            if not self.search_chat(contact_name):
                return {
                    "success": False,
                    "error": f"Contact '{contact_name}' not found "
                             "or chat failed to open",
                }

            # Chat is confirmed open (footer exists)
            # Wait a moment for any animations
            self.page.wait_for_timeout(1500)

            msg_input = self._find_message_input(retries=5)
            if not msg_input:
                return {
                    "success": False,
                    "error": "Message input not found - "
                             "check debug_no_msg_input.png",
                }

            # Click input, type, send
            self.logger.info("Clicking message input...")
            msg_input.click()
            self.page.wait_for_timeout(500)

            self.logger.info(f"Typing: {message_text[:50]}...")
            self.page.keyboard.insert_text(message_text)
            self.page.wait_for_timeout(500)

            self._screenshot("debug_before_send")

            # Try send button
            sent = False
            for sel in [
                '[data-testid="compose-btn-send"]',
                '[data-testid="send"]',
                'button[aria-label="Send"]',
                'span[data-icon="send"]',
            ]:
                btn = self.page.query_selector(sel)
                if btn:
                    try:
                        if btn.is_visible():
                            btn.click()
                            sent = True
                            self.logger.info(f"Sent via button: {sel}")
                            break
                    except Exception:
                        continue

            if not sent:
                self.page.keyboard.press("Enter")
                self.logger.info("Sent via Enter key")

            self.page.wait_for_timeout(2000)
            self._screenshot("debug_after_send")

            self.logger.info(f"Message sent to {contact_name}")
            return {
                "success": True,
                "recipient": contact_name,
                "message": message_text,
            }

        except Exception as e:
            self.logger.error(f"send_message failed: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return {"success": False, "error": str(e)}

    # === Reply ===
    def reply_to_message(self, contact_name, reply_text,
                         original_message=None):
        try:
            self.ensure_authenticated()
            self._wait_ready()
            if not self.search_chat(contact_name):
                return {
                    "success": False,
                    "error": f"Chat not found: {contact_name}",
                }
            self.page.wait_for_timeout(1500)
            msg_input = self._find_message_input(retries=4)
            if not msg_input:
                return {
                    "success": False,
                    "error": "Message input not found",
                }
            msg_input.click()
            self.page.wait_for_timeout(300)
            self.page.keyboard.insert_text(reply_text)
            self.page.wait_for_timeout(300)
            self.page.keyboard.press("Enter")
            self.page.wait_for_timeout(1500)
            self.logger.info(f"Reply sent to {contact_name}")
            return {"success": True, "recipient": contact_name}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # === Mark read ===
    def mark_as_read(self, contact_name):
        try:
            self.ensure_authenticated()
            self._wait_ready()
            if not self.search_chat(contact_name):
                return {
                    "success": False,
                    "error": f"Chat not found: {contact_name}",
                }
            self.page.wait_for_timeout(1500)
            return {"success": True, "contact": contact_name}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # === Media download ===
    def download_latest_media(self, contact_name):
        save_dir = self.media_dir
        save_dir.mkdir(parents=True, exist_ok=True)
        try:
            self.ensure_authenticated()
            if not self.search_chat(contact_name):
                return {
                    "success": False,
                    "error": f"Chat not found: {contact_name}",
                }
            self.page.wait_for_timeout(2200)
            media_el = None
            for sel in ['img[src^="blob:"]', 'video[src^="blob:"]']:
                els = self.page.query_selector_all(sel)
                if els:
                    media_el = els[-1]
                    break
            if not media_el:
                return {"success": False, "error": "No media found"}
            blob_url = (
                media_el.get_attribute("src")
                or media_el.evaluate("el => el.currentSrc || el.href")
            )
            if not blob_url or not blob_url.startswith("blob:"):
                return {"success": False, "error": "No blob URL"}
            b64 = self.page.evaluate('''async (url) => {
                const r = await fetch(url);
                const b = await r.blob();
                return new Promise(res => {
                    const rd = new FileReader();
                    rd.onloadend = () => res(
                        rd.result.split(',')[1]
                    );
                    rd.readAsDataURL(b);
                });
            }''', blob_url)
            if not b64:
                return {"success": False, "error": "Blob read failed"}
            tag = media_el.evaluate("el => el.tagName.toLowerCase()")
            ext = (
                ".jpg" if tag == "img"
                else ".mp4" if tag == "video"
                else ".file"
            )
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe = "".join(
                c if c.isalnum() else "_" for c in contact_name[:30]
            )
            full = save_dir / f"WA_{safe}_{ts}{ext}"
            with open(full, "wb") as f:
                f.write(base64.b64decode(b64))
            return {"success": True, "path": str(full)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # === Watcher ===
    def _wait_ready(self):
        """Ensure WhatsApp Web is loaded and ready."""
        self.page.wait_for_timeout(2000)
        if "web.whatsapp.com" not in self.page.url:
            self.page.goto(
                "https://web.whatsapp.com",
                wait_until="domcontentloaded",
                timeout=60000,
            )
            self.page.wait_for_timeout(4000)

    def _screenshot(self, name):
        """Take a screenshot for debugging."""
        try:
            path = f"debug_{name}.png"
            self.page.screenshot(path=path)
            self.logger.info(f"Screenshot saved: {path}")
        except Exception as e:
            self.logger.debug(f"Screenshot failed: {e}")

    def _close_browser(self):
        """Close browser and stop playwright."""
        if self.browser:
            self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()

    def check_for_updates(self):
        if not self.page:
            self.logger.error("No page object")
            return []
        try:
            self.logger.info("Checking for updates...")

            # Verify we're still on WhatsApp
            try:
                current_url = self.page.url
            except Exception:
                self.logger.error("Page handle dead - need restart")
                return []

            if "web.whatsapp.com" not in current_url:
                self.logger.info("Navigating to WhatsApp...")
                self.page.goto(
                    "https://web.whatsapp.com",
                    wait_until="domcontentloaded",
                    timeout=60000,
                )
                self.page.wait_for_timeout(4000)

            # Wait a moment for page to settle
            self.page.wait_for_timeout(2000)

            # Find chat list container
            self.logger.info("Looking for chat list...")
            cc = None
            for sel in [
                '#pane-side',
                '[data-testid="chat-list"]',
                'div[aria-label="Chat list"]',
                'div[role="list"]',
            ]:
                try:
                    elem = self.page.wait_for_selector(
                        sel, timeout=8000, state="visible"
                    )
                    if elem:
                        cc = elem
                        self.logger.info(f"Chat list found: {sel}")
                        break
                except Exception:
                    continue

            if not cc:
                self.logger.error(
                    "Chat list not found - is WhatsApp loaded?"
                )
                self._screenshot("debug_no_chatlist")
                return []

            # Get chat rows
            rows = []
            for rs in [
                'div[role="listitem"]',
                '[data-testid="cell-frame-container"]',
                'div[role="row"]',
            ]:
                r = cc.query_selector_all(rs)
                if r:
                    rows = r
                    self.logger.info(
                        f"Found {len(r)} chat rows using: {rs}"
                    )
                    break

            if not rows:
                self.logger.warning("No chat rows found")
                return []

            # Process rows
            msgs = []
            for row in rows:
                try:
                    ne = row.query_selector('span[title]')
                    name = (
                        ne.get_attribute("title").strip()
                        if ne else ""
                    )
                    if not name:
                        continue

                    # Get preview text
                    preview = ""
                    pe = row.query_selector(
                        'span[dir="auto"]:not([title])'
                    )
                    if pe:
                        preview = pe.inner_text().strip()
                    if not preview or len(preview) < 5:
                        lines = [
                            l.strip()
                            for l in row.inner_text().split('\n')
                            if l.strip()
                        ]
                        preview = (
                            lines[2] if len(lines) >= 3
                            else (
                                lines[-1] if len(lines) >= 2
                                else ""
                            )
                        )
                    preview = preview or "[N/A]"

                    # Check media
                    media = bool(row.query_selector(
                        '[data-icon="image"],'
                        '[data-icon="video"],'
                        '[data-icon="document"]'
                    ))

                    if (len(preview) > 3
                            and preview != "[N/A]"):
                        h = self._message_hash(name, preview)
                        if h not in self.processed_messages:
                            msgs.append({
                                'chat': name,
                                'text': preview,
                                'hash': h,
                                'has_media': media,
                                'media_type': (
                                    'unknown' if media else None
                                ),
                            })
                except Exception:
                    continue

            self.logger.info(
                f"Scan complete: {len(rows)} chats scanned, "
                f"{len(msgs)} new"
            )
            return msgs

        except Exception as e:
            self.logger.error(f"check_for_updates error: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return []

    def is_priority(self, text):
        return any(kw in text.lower() for kw in self.priority_keywords)

    def create_action_file(self, message):
        pri = (
            'high' if self.is_priority(message['text']) else 'normal'
        )
        kw = [
            k for k in self.priority_keywords
            if k in message['text'].lower()
        ]
        content = f"""---
type: whatsapp
from: {message['chat']}
received: {datetime.now().isoformat()}
priority: {pri}
status: pending
keywords: {', '.join(kw[:5]) or 'none'}
---

## Message
**From:** {message['chat']}
**Detected:** {datetime.now().strftime('%Y-%m-%d %I:%M %p')}
> {message['text']}

## Actions
- [ ] Review
- [ ] Reply
"""
        safe = "".join(
            c if c.isalnum() else "_" for c in message['chat'][:30]
        )
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        path = self.needs_action / f"WHATSAPP_{safe}_{ts}.md"
        self.needs_action.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
        self.processed_messages.add(message['hash'])
        self._save_processed_messages()
        return path

    def run(self):
        self.logger.info("Starting WhatsApp Watcher...")
        if not self.authenticate():
            self.logger.error("Auth failed")
            return

        self._wait_ready()

        # First run baseline
        is_first = (
            not self.processed_ids_file.exists()
            or len(self.processed_messages) == 0
        )
        if is_first:
            self.logger.info("=" * 50)
            self.logger.info("FIRST RUN - scanning existing chats as baseline")
            self.logger.info("=" * 50)
            try:
                msgs = self.check_for_updates()
                self.logger.info(
                    f"Found {len(msgs)} existing chats - "
                    f"marking as already seen"
                )
                for m in msgs:
                    self.processed_messages.add(m['hash'])
                self._save_processed_messages()
                self.logger.info(
                    f"Baseline complete: {len(self.processed_messages)} "
                    f"messages registered"
                )
                self.logger.info(
                    "Only NEW messages will create action files from now on"
                )
            except Exception as e:
                self.logger.error(f"Initial scan failed: {e}")

        self.running = True
        cycle = 0

        self.logger.info("=" * 50)
        self.logger.info(
            f"MONITORING STARTED - checking every "
            f"{self.check_interval} seconds"
        )
        self.logger.info(f"Action files go to: {self.needs_action}")
        self.logger.info("Press Ctrl+C to stop")
        self.logger.info("=" * 50)

        try:
            while self.running:
                cycle += 1
                try:
                    self.logger.info(
                        f"--- Check cycle {cycle} ---"
                    )
                    msgs = self.check_for_updates()

                    if msgs:
                        self.logger.info(
                            f"[!] {len(msgs)} NEW message(s) detected!"
                        )
                        for m in msgs:
                            pri = (
                                "HIGH"
                                if self.is_priority(m['text'])
                                else "normal"
                            )
                            self.logger.info(
                                f"  {pri} | {m['chat']} | "
                                f"{m['text'][:60]}"
                            )
                            path = self.create_action_file(m)
                            self.logger.info(
                                f"  -> Action file: {path.name}"
                            )
                    else:
                        self.logger.info("No new messages")

                    self.logger.info(
                        f"Next check in {self.check_interval}s..."
                    )
                    time.sleep(self.check_interval)

                except KeyboardInterrupt:
                    self.logger.info("Ctrl+C received - stopping...")
                    break
                except Exception as e:
                    self.logger.error(f"Cycle {cycle} error: {e}")
                    import traceback
                    self.logger.error(traceback.format_exc())
                    self.logger.info(
                        f"Retrying in {self.check_interval}s..."
                    )
                    time.sleep(self.check_interval)
        finally:
            self.running = False
            self._close_browser()
            self.logger.info("Watcher stopped")

    def stop(self):
        self.running = False


def main():
    parser = argparse.ArgumentParser(description='WhatsApp Watcher')
    parser.add_argument('command', choices=[
        'start', 'check', 'auth', 'status', 'download',
        'send', 'reply', 'mark-read',
    ])
    parser.add_argument('--vault', default=None)
    parser.add_argument('--interval', type=int, default=CHECK_INTERVAL)
    parser.add_argument('--contact', help='Contact name')
    parser.add_argument('--message', help='Message text')
    args = parser.parse_args()

    watcher = WhatsAppWatcher(args.vault, args.interval)

    if args.command == 'start':
        watcher.run()
    elif args.command == 'check':
        if watcher.authenticate():
            for m in watcher.check_for_updates():
                watcher.create_action_file(m)
    elif args.command == 'auth':
        ok = watcher.authenticate()
        print("OK" if ok else "FAILED")
        sys.exit(0 if ok else 1)
    elif args.command == 'status':
        print(f"  Vault     : {watcher.vault_path}")
        print(f"  Session   : {SESSION_DIR}")
        print(f"  Processed : {len(watcher.processed_messages)}")
        print(
            f"  Playwright: "
            f"{'Yes' if PLAYWRIGHT_AVAILABLE else 'No'}"
        )
    elif args.command == 'download':
        if not args.contact:
            print("--contact required")
            sys.exit(1)
        if watcher.authenticate():
            print(json.dumps(
                watcher.download_latest_media(args.contact), indent=2
            ))
    elif args.command == 'send':
        if not args.contact or not args.message:
            print("--contact and --message required")
            sys.exit(1)
        result = watcher.send_message(args.contact, args.message)
        print(json.dumps(result, indent=2))
    elif args.command == 'reply':
        if not args.contact or not args.message:
            print("--contact and --message required")
            sys.exit(1)
        result = watcher.reply_to_message(args.contact, args.message)
        print(json.dumps(result, indent=2))
    elif args.command == 'mark-read':
        if not args.contact:
            print("--contact required")
            sys.exit(1)
        result = watcher.mark_as_read(args.contact)
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()