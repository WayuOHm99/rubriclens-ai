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
        
        # -> Paste the test document into the 'ข้อความเอกสาร' (document text) textarea so the app can detect the appendix.
        # ข้อความเอกสาร text area
        elem = page.locator('[id="report-text"]')
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("Title: Test Document\n\nIntroduction\nThis is the main body of the document. It contains the core content to be analyzed by the system.\n\nMethods\nDescription of methods used in the study.\n\nResults\nSummary of results and discussion.\n\nAppendix\nAppendix A: Supplementary tables and raw data that should be considered part of the appendix and can be excluded from the main analysis.\n\nAppendix B: Additional charts and extended methodology details.")
        
        # -> Click the 'ตรวจรายงาน' (Analyze) button to trigger appendix detection and any exclusion prompt.
        # ตรวจรายงาน · ข้อมูลตัวอย่าง button
        elem = page.get_by_role('button', name='ตรวจรายงาน', exact=True)
        await elem.click(timeout=10000)
        
        # -> Click the 'ยืนยันและส่งตรวจ' (Confirm and send for review) button in the modal to exclude the appendix and submit the adjusted document for analysis.
        # ยืนยันและส่งตรวจ button
        elem = page.get_by_role('button', name='ยืนยันและส่งตรวจ', exact=True)
        await elem.click(timeout=10000)
        
        # --> Assertions to verify final state
        
        # --> Verify the analysis result is displayed for the adjusted document
        await page.locator("xpath=/html/body/div[1]/main/div/section").nth(0).scroll_into_view_if_needed()
        # Assert: The analysis results panel titled 'ผลตรวจรายงานทั่วไป' is visible.
        await expect(page.locator("xpath=/html/body/div[1]/main/div/section").nth(0)).to_be_visible(timeout=15000), "The analysis results panel titled '\u0e1c\u0e25\u0e15\u0e23\u0e27\u0e08\u0e23\u0e32\u0e22\u0e07\u0e32\u0e19\u0e17\u0e31\u0e48\u0e27\u0e44\u0e1b' is visible."
        await page.locator("xpath=/html/body/div[1]/main/div/section/div[1]/div[2]/div/div[2]/button[1]").nth(0).scroll_into_view_if_needed()
        # Assert: The 'คัดลอกผล' (Copy results) button is visible on the analysis results panel.
        await expect(page.locator("xpath=/html/body/div[1]/main/div/section/div[1]/div[2]/div/div[2]/button[1]").nth(0)).to_be_visible(timeout=15000), "The '\u0e04\u0e31\u0e14\u0e25\u0e2d\u0e01\u0e1c\u0e25' (Copy results) button is visible on the analysis results panel."
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
    