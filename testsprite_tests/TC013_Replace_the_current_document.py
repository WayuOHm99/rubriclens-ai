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
        
        # -> Wait for the app to finish loading and reveal the 'Paste report' document input area.
        await page.goto("http://localhost:5173/")
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=5000)
        except Exception:
            pass
        
        # -> Paste a sample report into the 'ข้อความเอกสาร' (document text) textarea.
        # ข้อความเอกสาร text area
        elem = page.locator('[id="report-text"]')
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("Sample QA report: This is a short test document used to verify the document input, removal, and clearing behavior of the analyzer.")
        
        # -> Click the 'เริ่มใหม่' (Start over) button to remove the current document from the textarea.
        # เริ่มใหม่ button
        elem = page.get_by_role('button', name='เริ่มใหม่', exact=True)
        await elem.click(timeout=10000)
        
        # --> Assertions to verify final state
        
        # --> Verify the document input is cleared
        # Assert: The document textarea is empty (cleared).
        await expect(page.locator("xpath=/html/body/div/main/div/div[2]/div/div[2]/div[1]/textarea").nth(0)).to_have_value("", timeout=15000), "The document textarea is empty (cleared)."
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
    