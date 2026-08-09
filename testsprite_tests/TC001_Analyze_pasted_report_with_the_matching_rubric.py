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
        
        # -> Open the 'ประเภทงาน' (Document type) dropdown so the correct document type can be selected.
        # รายงานทั่วไป โครงงาน รายงานวิจัย dropdown
        elem = page.locator('[id="document-type"]')
        await elem.click(timeout=10000)
        
        # -> Paste sample report text into the 'ข้อความเอกสาร' textarea and then click the 'ตรวจรายงาน' button to run the analysis.
        # ข้อความเอกสาร text area
        elem = page.locator('[id="report-text"]')
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("\u0e1a\u0e17\u0e19\u0e33: \u0e23\u0e32\u0e22\u0e07\u0e32\u0e19\u0e19\u0e35\u0e49\u0e19\u0e33\u0e40\u0e2a\u0e19\u0e2d\u0e1c\u0e25\u0e01\u0e32\u0e23\u0e2a\u0e33\u0e23\u0e27\u0e08\u0e40\u0e01\u0e35\u0e48\u0e22\u0e27\u0e01\u0e31\u0e1a\u0e01\u0e32\u0e23\u0e08\u0e31\u0e14\u0e01\u0e32\u0e23\u0e02\u0e22\u0e30\u0e43\u0e19\u0e0a\u0e38\u0e21\u0e0a\u0e19 \u0e27\u0e34\u0e40\u0e04\u0e23\u0e32\u0e30\u0e2b\u0e4c\u0e02\u0e49\u0e2d\u0e21\u0e39\u0e25\u0e08\u0e32\u0e01\u0e41\u0e1a\u0e1a\u0e2a\u0e2d\u0e1a\u0e16\u0e32\u0e21\u0e41\u0e25\u0e30\u0e01\u0e32\u0e23\u0e2a\u0e31\u0e07\u0e40\u0e01\u0e15 \u0e42\u0e14\u0e22\u0e41\u0e1a\u0e48\u0e07\u0e40\u0e1b\u0e47\u0e19\u0e1a\u0e23\u0e34\u0e1a\u0e17 \u0e27\u0e34\u0e18\u0e35\u0e01\u0e32\u0e23 \u0e1c\u0e25\u0e01\u0e32\u0e23\u0e28\u0e36\u0e01\u0e29\u0e32 \u0e41\u0e25\u0e30\u0e02\u0e49\u0e2d\u0e40\u0e2a\u0e19\u0e2d\u0e41\u0e19\u0e30\n\u0e2a\u0e23\u0e38\u0e1b: \u0e1e\u0e1a\u0e1b\u0e31\u0e0d\u0e2b\u0e32\u0e01\u0e32\u0e23\u0e04\u0e31\u0e14\u0e41\u0e22\u0e01\u0e02\u0e22\u0e30\u0e44\u0e21\u0e48\u0e40\u0e1b\u0e47\u0e19\u0e23\u0e30\u0e1a\u0e1a\u0e41\u0e25\u0e30\u0e01\u0e32\u0e23\u0e02\u0e32\u0e14\u0e04\u0e27\u0e32\u0e21\u0e23\u0e39\u0e49\u0e02\u0e2d\u0e07\u0e1b\u0e23\u0e30\u0e0a\u0e32\u0e0a\u0e19 \u0e08\u0e36\u0e07\u0e41\u0e19\u0e30\u0e19\u0e33\u0e01\u0e32\u0e23\u0e08\u0e31\u0e14\u0e01\u0e34\u0e08\u0e01\u0e23\u0e23\u0e21\u0e43\u0e2b\u0e49\u0e04\u0e27\u0e32\u0e21\u0e23\u0e39\u0e49\u0e41\u0e25\u0e30\u0e15\u0e34\u0e14\u0e15\u0e31\u0e49\u0e07\u0e16\u0e31\u0e07\u0e41\u0e22\u0e01\u0e1b\u0e23\u0e30\u0e40\u0e20\u0e17\u0e43\u0e19\u0e08\u0e38\u0e14\u0e2a\u0e33\u0e04\u0e31\u0e0d\u0e02\u0e2d\u0e07\u0e0a\u0e38\u0e21\u0e0a\u0e19")
        
        # -> Paste sample report text into the 'ข้อความเอกสาร' textarea and then click the 'ตรวจรายงาน' button to run the analysis.
        # ตรวจรายงาน · ข้อมูลตัวอย่าง button
        elem = page.get_by_role('button', name='ตรวจรายงาน', exact=True)
        await elem.click(timeout=10000)
        
        # --> Assertions to verify final state
        
        # --> Verify an overall weighted score is displayed
        # Assert: Overall weighted score '80%' is displayed in the results panel.
        await expect(page.locator("xpath=/html/body/div/main/div/section").nth(0)).to_contain_text("80%", timeout=15000), "Overall weighted score '80%' is displayed in the results panel."
        
        # --> Verify criterion-level feedback and recommendations are displayed
        await page.locator("xpath=/html/body/div/main/div/section").nth(0).scroll_into_view_if_needed()
        # Assert: The analysis results panel is visible on the page.
        await expect(page.locator("xpath=/html/body/div/main/div/section").nth(0)).to_be_visible(timeout=15000), "The analysis results panel is visible on the page."
        # Assert: Criterion-level feedback for 'บทนำและบริบท' is displayed.
        await expect(page.locator("xpath=/html/body/div/main/div/section").nth(0)).to_contain_text("\u0e1a\u0e17\u0e19\u0e33\u0e41\u0e25\u0e30\u0e1a\u0e23\u0e34\u0e1a\u0e17", timeout=15000), "Criterion-level feedback for '\u0e1a\u0e17\u0e19\u0e33\u0e41\u0e25\u0e30\u0e1a\u0e23\u0e34\u0e1a\u0e17' is displayed."
        # Assert: Recommendations (marked by 'ควรทำ:') are shown for the criteria.
        await expect(page.locator("xpath=/html/body/div/main/div/section").nth(0)).to_contain_text("\u0e04\u0e27\u0e23\u0e17\u0e33:", timeout=15000), "Recommendations (marked by '\u0e04\u0e27\u0e23\u0e17\u0e33:') are shown for the criteria."
        await asyncio.sleep(5)

    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if pw:
            await pw.stop()

asyncio.run(run_test())
    