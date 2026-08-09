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
        
        # -> Reload the current page (RubricLensAi | ตรวจเอกสารให้คร) to attempt to load the SPA UI.
        await page.goto("http://localhost:5173/")
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=5000)
        except Exception:
            pass
        
        # -> Open the 'ประเภทงาน' (Document type) dropdown so a different template (e.g., 'โครงงาน') can be selected.
        # รายงานทั่วไป โครงงาน รายงานวิจัย dropdown
        elem = page.locator('[id="document-type"]')
        await elem.click(timeout=10000)
        
        # -> Select 'โครงงาน' from the 'ประเภทงาน' (Document type) dropdown and allow the UI to update.
        # รายงานทั่วไป โครงงาน รายงานวิจัย dropdown
        elem = page.locator("xpath=/html/body/div/main/div/div[3]/div[2]/div/label/select").nth(0)
        await elem.wait_for(state="visible", timeout=10000)
        await elem.select_option("")
        
        # --> Assertions to verify final state
        
        # --> Verify the rubric changes to match the selected template
        # Assert: Rubric template is set to 'เกณฑ์โครงงาน' matching the selected template.
        await expect(page.locator("xpath=/html/body/div/main/div/div[3]/div[2]/div[1]/label[2]/select").nth(0)).to_have_text("\u0e40\u0e01\u0e13\u0e11\u0e4c\u0e42\u0e04\u0e23\u0e07\u0e07\u0e32\u0e19", timeout=15000), "Rubric template is set to '\u0e40\u0e01\u0e13\u0e11\u0e4c\u0e42\u0e04\u0e23\u0e07\u0e07\u0e32\u0e19' matching the selected template."
        
        # --> Verify document-specific guidance is displayed
        # Assert: Document-specific guidance displays the 'จุดเน้น:' label.
        await expect(page.locator("xpath=/html/body/div/main/div/div[3]/div[2]/div[2]/p[2]/span").nth(0)).to_have_text("\u0e08\u0e38\u0e14\u0e40\u0e19\u0e49\u0e19:", timeout=15000), "Document-specific guidance displays the '\u0e08\u0e38\u0e14\u0e40\u0e19\u0e49\u0e19:' label."
        # Assert: Document-specific guidance displays the 'ข้อจำกัด:' label.
        await expect(page.locator("xpath=/html/body/div/main/div/div[3]/div[2]/div[2]/p[3]/span").nth(0)).to_have_text("\u0e02\u0e49\u0e2d\u0e08\u0e33\u0e01\u0e31\u0e14:", timeout=15000), "Document-specific guidance displays the '\u0e02\u0e49\u0e2d\u0e08\u0e33\u0e01\u0e31\u0e14:' label."
        await asyncio.sleep(5)

    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if pw:
            await pw.stop()

asyncio.run(run_test())
    