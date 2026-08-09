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
        
        # -> Wait for the RubricLensAi page to finish loading and then reload the page if the UI remains blank so the rubric controls become visible.
        await page.goto("http://localhost:5173/")
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=5000)
        except Exception:
            pass
        
        # -> Click the 'แก้ไขหัวข้อและน้ำหนัก' button to open the advanced rubric controls.
        # แก้ไขหัวข้อและน้ำหนัก button
        elem = page.get_by_role('button', name='แก้ไขหัวข้อและน้ำหนัก', exact=True)
        await elem.click(timeout=10000)
        
        # -> Click the 'เพิ่มหัวข้อใหม่' button to add a new criterion.
        # เพิ่มหัวข้อใหม่ button
        elem = page.get_by_role('button', name='เพิ่มหัวข้อใหม่', exact=True)
        await elem.click(timeout=10000)
        
        # -> Click the 'ลบหัวข้อใหม่' (Delete) button to remove the newly added criterion.
        # ลบหัวข้อ button
        elem = page.get_by_role('button', name='ลบ หัวข้อใหม่', exact=True)
        await elem.click(timeout=10000)
        
        # --> Assertions to verify final state
        
        # --> Verify the updated rubric is displayed
        await page.locator("xpath=/html/body/div/main/div/div[3]/div[2]/button").nth(0).scroll_into_view_if_needed()
        # Assert: Advanced rubric controls are open and the 'ซ่อนการตั้งค่าขั้นสูง' button is visible.
        await expect(page.locator("xpath=/html/body/div/main/div/div[3]/div[2]/button").nth(0)).to_be_visible(timeout=15000), "Advanced rubric controls are open and the '\u0e0b\u0e48\u0e2d\u0e19\u0e01\u0e32\u0e23\u0e15\u0e31\u0e49\u0e07\u0e04\u0e48\u0e32\u0e02\u0e31\u0e49\u0e19\u0e2a\u0e39\u0e07' button is visible."
        await page.locator("xpath=/html/body/div/main/div/div[3]/div[2]/div[4]/button").nth(0).scroll_into_view_if_needed()
        # Assert: The 'เพิ่มหัวข้อใหม่' (add criterion) control is visible in the rubric area.
        await expect(page.locator("xpath=/html/body/div/main/div/div[3]/div[2]/div[4]/button").nth(0)).to_be_visible(timeout=15000), "The '\u0e40\u0e1e\u0e34\u0e48\u0e21\u0e2b\u0e31\u0e27\u0e02\u0e49\u0e2d\u0e43\u0e2b\u0e21\u0e48' (add criterion) control is visible in the rubric area."
        # Assert: The rubric displays 'ใช้ 8 / 8 หัวข้อ', confirming 8 active criteria and that the updated rubric is shown.
        await expect(page.locator("xpath=/html/body/div").nth(0)).to_contain_text("\u0e43\u0e0a\u0e49 8 / 8 \u0e2b\u0e31\u0e27\u0e02\u0e49\u0e2d", timeout=15000), "The rubric displays '\u0e43\u0e0a\u0e49 8 / 8 \u0e2b\u0e31\u0e27\u0e02\u0e49\u0e2d', confirming 8 active criteria and that the updated rubric is shown."
        
        # --> Verify the criterion list reflects the add and remove changes
        # Assert: Rubric contains the criterion 'บทนำและบริบท'.
        await expect(page.locator("xpath=/html/body/div/main/div/div[3]/div[2]/div[4]/div[1]/div/label[1]/input").nth(0)).to_have_value("\u0e1a\u0e17\u0e19\u0e33\u0e41\u0e25\u0e30\u0e1a\u0e23\u0e34\u0e1a\u0e17", timeout=15000), "Rubric contains the criterion '\u0e1a\u0e17\u0e19\u0e33\u0e41\u0e25\u0e30\u0e1a\u0e23\u0e34\u0e1a\u0e17'."
        # Assert: Rubric contains the criterion 'จุดมุ่งหมายของรายงาน'.
        await expect(page.locator("xpath=/html/body/div/main/div/div[3]/div[2]/div[4]/div[2]/div/label[1]/input").nth(0)).to_have_value("\u0e08\u0e38\u0e14\u0e21\u0e38\u0e48\u0e07\u0e2b\u0e21\u0e32\u0e22\u0e02\u0e2d\u0e07\u0e23\u0e32\u0e22\u0e07\u0e32\u0e19", timeout=15000), "Rubric contains the criterion '\u0e08\u0e38\u0e14\u0e21\u0e38\u0e48\u0e07\u0e2b\u0e21\u0e32\u0e22\u0e02\u0e2d\u0e07\u0e23\u0e32\u0e22\u0e07\u0e32\u0e19'."
        # Assert: Rubric contains the criterion 'ความครบถ้วนและคุณภาพข้อมูล'.
        await expect(page.locator("xpath=/html/body/div/main/div/div[3]/div[2]/div[4]/div[3]/div/label[1]/input").nth(0)).to_have_value("\u0e04\u0e27\u0e32\u0e21\u0e04\u0e23\u0e1a\u0e16\u0e49\u0e27\u0e19\u0e41\u0e25\u0e30\u0e04\u0e38\u0e13\u0e20\u0e32\u0e1e\u0e02\u0e49\u0e2d\u0e21\u0e39\u0e25", timeout=15000), "Rubric contains the criterion '\u0e04\u0e27\u0e32\u0e21\u0e04\u0e23\u0e1a\u0e16\u0e49\u0e27\u0e19\u0e41\u0e25\u0e30\u0e04\u0e38\u0e13\u0e20\u0e32\u0e1e\u0e02\u0e49\u0e2d\u0e21\u0e39\u0e25'."
        # Assert: Rubric contains the criterion 'การจัดลำดับและการเชื่อมโยง'.
        await expect(page.locator("xpath=/html/body/div/main/div/div[3]/div[2]/div[4]/div[4]/div/label[1]/input").nth(0)).to_have_value("\u0e01\u0e32\u0e23\u0e08\u0e31\u0e14\u0e25\u0e33\u0e14\u0e31\u0e1a\u0e41\u0e25\u0e30\u0e01\u0e32\u0e23\u0e40\u0e0a\u0e37\u0e48\u0e2d\u0e21\u0e42\u0e22\u0e07", timeout=15000), "Rubric contains the criterion '\u0e01\u0e32\u0e23\u0e08\u0e31\u0e14\u0e25\u0e33\u0e14\u0e31\u0e1a\u0e41\u0e25\u0e30\u0e01\u0e32\u0e23\u0e40\u0e0a\u0e37\u0e48\u0e2d\u0e21\u0e42\u0e22\u0e07'."
        # Assert: Rubric contains the criterion 'การอธิบายและการสื่อสาร'.
        await expect(page.locator("xpath=/html/body/div/main/div/div[3]/div[2]/div[4]/div[5]/div/label[1]/input").nth(0)).to_have_value("\u0e01\u0e32\u0e23\u0e2d\u0e18\u0e34\u0e1a\u0e32\u0e22\u0e41\u0e25\u0e30\u0e01\u0e32\u0e23\u0e2a\u0e37\u0e48\u0e2d\u0e2a\u0e32\u0e23", timeout=15000), "Rubric contains the criterion '\u0e01\u0e32\u0e23\u0e2d\u0e18\u0e34\u0e1a\u0e32\u0e22\u0e41\u0e25\u0e30\u0e01\u0e32\u0e23\u0e2a\u0e37\u0e48\u0e2d\u0e2a\u0e32\u0e23'."
        # Assert: Rubric contains the criterion 'การวิเคราะห์และสังเคราะห์'.
        await expect(page.locator("xpath=/html/body/div/main/div/div[3]/div[2]/div[4]/div[6]/div/label[1]/input").nth(0)).to_have_value("\u0e01\u0e32\u0e23\u0e27\u0e34\u0e40\u0e04\u0e23\u0e32\u0e30\u0e2b\u0e4c\u0e41\u0e25\u0e30\u0e2a\u0e31\u0e07\u0e40\u0e04\u0e23\u0e32\u0e30\u0e2b\u0e4c", timeout=15000), "Rubric contains the criterion '\u0e01\u0e32\u0e23\u0e27\u0e34\u0e40\u0e04\u0e23\u0e32\u0e30\u0e2b\u0e4c\u0e41\u0e25\u0e30\u0e2a\u0e31\u0e07\u0e40\u0e04\u0e23\u0e32\u0e30\u0e2b\u0e4c'."
        # Assert: Rubric contains the criterion 'บทสรุป'.
        await expect(page.locator("xpath=/html/body/div/main/div/div[3]/div[2]/div[4]/div[7]/div/label[1]/input").nth(0)).to_have_value("\u0e1a\u0e17\u0e2a\u0e23\u0e38\u0e1b", timeout=15000), "Rubric contains the criterion '\u0e1a\u0e17\u0e2a\u0e23\u0e38\u0e1b'."
        # Assert: Rubric contains the criterion 'การอ้างอิงและแหล่งที่มา'.
        await expect(page.locator("xpath=/html/body/div/main/div/div[3]/div[2]/div[4]/div[8]/div/label[1]/input").nth(0)).to_have_value("\u0e01\u0e32\u0e23\u0e2d\u0e49\u0e32\u0e07\u0e2d\u0e34\u0e07\u0e41\u0e25\u0e30\u0e41\u0e2b\u0e25\u0e48\u0e07\u0e17\u0e35\u0e48\u0e21\u0e32", timeout=15000), "Rubric contains the criterion '\u0e01\u0e32\u0e23\u0e2d\u0e49\u0e32\u0e07\u0e2d\u0e34\u0e07\u0e41\u0e25\u0e30\u0e41\u0e2b\u0e25\u0e48\u0e07\u0e17\u0e35\u0e48\u0e21\u0e32'."
        await asyncio.sleep(5)

    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if pw:
            await pw.stop()

asyncio.run(run_test())
    