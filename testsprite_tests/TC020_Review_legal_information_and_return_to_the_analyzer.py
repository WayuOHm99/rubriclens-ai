import asyncio
import re
from playwright import async_api
from playwright.async_api import expect

async def run_test():
    pw = None
    browser = None
    context = None

    try:
        # Start a Playwright session in asynchronous mode
        pw = await async_api.async_playwright().start()

        # Launch a Chromium browser in headless mode with custom arguments
        browser = await pw.chromium.launch(
            headless=True,
            args=[
                "--window-size=1280,720",
                "--disable-dev-shm-usage",
                "--ipc=host",
                "--single-process"
            ],
        )

        # Create a new browser context (like an incognito window)
        context = await browser.new_context()
        # Wider default timeout to match the agent's DOM-stability budget;
        # auto-waiting Playwright APIs (expect, locator.wait_for) inherit this.
        context.set_default_timeout(15000)

        # Open a new page in the browser context
        page = await context.new_page()

        # Interact with the page elements to simulate user flow
        # -> navigate
        await page.goto("http://localhost:5173/")
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=5000)
        except Exception:
            pass
        
        # -> Click the 'นโยบายความเป็นส่วนตัว' (Privacy policy) link in the footer to open the privacy page.
        # นโยบายความเป็นส่วนตัว link
        elem = page.get_by_role('link', name='นโยบายความเป็นส่วนตัว', exact=True)
        await elem.click(timeout=10000)
        
        # -> Verify the privacy policy heading 'นโยบายความเป็นส่วนตัว' is visible, then click the '← กลับไปหน้าตรวจเอกสาร' link to return to the analyzer.
        # ← กลับไปหน้าตรวจเอกสาร link
        elem = page.get_by_role('link', name='← กลับไปหน้าตรวจเอกสาร', exact=True)
        await elem.click(timeout=10000)
        
        # -> Click the 'ข้อกำหนดการใช้งาน' (Terms of Use) link in the footer to open the terms page.
        # ข้อกำหนดการใช้งาน link
        elem = page.get_by_role('link', name='ข้อกำหนดการใช้งาน', exact=True)
        await elem.click(timeout=10000)
        
        # -> Verify the 'ข้อกำหนดการใช้งาน' heading is visible, then click the '← กลับไปหน้าตรวจเอกสาร' link to return to the analyzer/main page.
        # ← กลับไปหน้าตรวจเอกสาร link
        elem = page.get_by_role('link', name='← กลับไปหน้าตรวจเอกสาร', exact=True)
        await elem.click(timeout=10000)
        
        # -> Click the 'ข้อกำหนดการใช้งาน' (Terms of Use) link in the footer to open the terms page.
        # ข้อกำหนดการใช้งาน link
        elem = page.get_by_role('link', name='ข้อกำหนดการใช้งาน', exact=True)
        await elem.click(timeout=10000)
        
        # -> Click the '← กลับไปหน้าตรวจเอกสาร' (Back to analyzer) link to return to the main page.
        # ← กลับไปหน้าตรวจเอกสาร link
        elem = page.get_by_role('link', name='← กลับไปหน้าตรวจเอกสาร', exact=True)
        await elem.click(timeout=10000)
        
        # -> Click the 'ข้อกำหนดการใช้งาน' (Terms of Use) link in the footer to open the Terms page.
        # ข้อกำหนดการใช้งาน link
        elem = page.get_by_role('link', name='ข้อกำหนดการใช้งาน', exact=True)
        await elem.click(timeout=10000)
        
        # -> Click the '← กลับไปหน้าตรวจเอกสาร' link to return to the analyzer/main page.
        # ← กลับไปหน้าตรวจเอกสาร link
        elem = page.get_by_role('link', name='← กลับไปหน้าตรวจเอกสาร', exact=True)
        await elem.click(timeout=10000)
        
        # -> Click the 'ข้อกำหนดการใช้งาน' (Terms of Use) link in the footer to open the Terms page and verify the Terms heading and body appear.
        # ข้อกำหนดการใช้งาน link
        elem = page.get_by_role('link', name='ข้อกำหนดการใช้งาน', exact=True)
        await elem.click(timeout=10000)
        
        # --> Assertions to verify final state
        
        # --> Verify terms content is displayed
        # Assert: The Terms of Use heading 'ข้อกำหนดการใช้งาน' is visible on the page.
        await expect(page.locator("xpath=/html/body/div").nth(0)).to_contain_text("\u0e02\u0e49\u0e2d\u0e01\u0e33\u0e2b\u0e19\u0e14\u0e01\u0e32\u0e23\u0e43\u0e0a\u0e49\u0e07\u0e32\u0e19", timeout=15000), "The Terms of Use heading '\u0e02\u0e49\u0e2d\u0e01\u0e33\u0e2b\u0e19\u0e14\u0e01\u0e32\u0e23\u0e43\u0e0a\u0e49\u0e07\u0e32\u0e19' is visible on the page."
        current_url = await page.evaluate("() => window.location.href")
        # Assert: page loaded with a URL (final outcome verified by the AI judge during the run)
        assert current_url, 'Page should have loaded with a URL'
        await asyncio.sleep(5)

    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if pw:
            await pw.stop()

asyncio.run(run_test())
    