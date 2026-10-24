from playwright.sync_api import sync_playwright
from ..config import BROWSER_HEADLESS, MAX_TEXT_CHARS, BROWSER_TIMEOUT_MS, BROWSER_PROFILE_DIR

class BrowserManager:
    def __init__(self): self.pw=None; self.context=None; self.page=None
    def start(self):
        if self.page: return
        self.pw=sync_playwright().start()
        self.context=self.pw.chromium.launch_persistent_context(str(BROWSER_PROFILE_DIR),headless=BROWSER_HEADLESS)
        self.page=self.context.pages[0] if self.context.pages else self.context.new_page()
    def goto(self,url):
        self.start()
        if not url.startswith(('http://','https://')): url='https://'+url
        self.page.goto(url,wait_until='domcontentloaded',timeout=BROWSER_TIMEOUT_MS)
        return self.snapshot()
    def snapshot(self):
        self.start(); text=self.page.locator('body').inner_text(timeout=10000)
        return {'ok':True,'url':self.page.url,'title':self.page.title(),'text':text[:MAX_TEXT_CHARS]}
    def semantic_fill(self,target,value):
        self.start(); loc=self._locator(target); loc.first.fill(value); return {'ok':True,'target':target}
    def semantic_click(self,target):
        self.start(); loc=self._locator(target); loc.first.click(); return self.snapshot()
    def _locator(self,target):
        p=self.page
        # Prefer exact/accessible text, then labels/placeholders, then CSS.
        for maker in [lambda:p.get_by_role('button',name=target,exact=True),lambda:p.get_by_label(target,exact=True),lambda:p.get_by_placeholder(target,exact=True),lambda:p.get_by_text(target,exact=True),lambda:p.locator(target)]:
            try:
                if maker().count()>0: return maker()
            except Exception: pass
        return p.get_by_text(target)
    def close(self):
        try:
            if self.context:self.context.close()
            if self.pw:self.pw.stop()
        finally:self.pw=self.context=self.page=None
browser=BrowserManager()
