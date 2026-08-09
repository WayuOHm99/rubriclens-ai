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
        
        # -> Paste a document containing an 'Appendix' heading into the document text area (placeholder: 'วางเนื้อหาเอกสารที่นี่…') and wait for the app to show any appendix detection prompt.
        # ข้อความเอกสาร text area
        elem = page.locator('[id="report-text"]')
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("Title: The Impact of Study Habits on Academic Performance\n\nAbstract:\nThis short report examines common study habits and their correlation with academic outcomes. Methods included surveys and analysis of study schedules.\n\n1. Introduction\nEffective study habits are associated with higher performance. This report summarizes the findings from a class-wide survey.\n\n2. Methods\nA questionnaire was administered to 120 students asking about hours studied per week, preferred study environment, and use of group study.\n\n3. Results\nStudents who scheduled regular study blocks tended to report higher grades. Group study was beneficial for conceptual subjects.\n\n4. Discussion\nRecommendations include creating a weekly study plan and mixing individual and group study sessions.\n\nAppendix\nAppendix A: Survey Instrument\nQuestion 1: How many hours per week do you study?\nQuestion 2: Where do you usually study?\n\nAppendix B: Raw Survey Responses\n- Student 1: 10 hours, library\n- Student 2: 6 hours, home")
        
        # -> Click the 'ตรวจรายงาน' (Analyze) button to trigger any appendix-detection prompt.
        # ตรวจรายงาน · ข้อมูลตัวอย่าง button
        elem = page.get_by_role('button', name='ตรวจรายงาน', exact=True)
        await elem.click(timeout=10000)
        
        # -> Click the 'กลับไปแก้ข้อความ' (Go back to edit) button to cancel appendix exclusion and return to the editor for further editing.
        # กลับไปแก้ข้อความ button
        elem = page.get_by_role('button', name='กลับไปแก้ข้อความ', exact=True)
        await elem.click(timeout=10000)
        
        # -> Append a character to the document textarea (placeholder: 'วางเนื้อหาเอกสารที่นี่…') to confirm it is editable and the appendix-exclusion modal is closed, then find the text 'Appendix' on the page.
        # ข้อความเอกสาร text area
        elem = page.locator('[id="report-text"]')
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill(" ")
        
        # -> Verify the document textarea is editable and that the appendix-detection modal is closed by focusing the textarea and typing a visible character into it.
        # ข้อความเอกสาร text area
        elem = page.locator('[id="report-text"]')
        await elem.click(timeout=10000)
        
        # -> Verify the document textarea is editable and that the appendix-detection modal is closed by focusing the textarea and typing a visible character into it.
        # ข้อความเอกสาร text area
        elem = page.locator('[id="report-text"]')
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill(".")
        
        # -> Open the 'ประเภทงาน' (Document type) dropdown so the option 'รายงานทั่วไป' can be selected.
        # รายงานทั่วไป โครงงาน รายงานวิจัย dropdown
        elem = page.locator('[id="document-type"]')
        await elem.click(timeout=10000)
        
        # -> Select 'รายงานทั่วไป' from the 'ประเภทงาน' (Document type) dropdown so the document type matches the pasted report.
        # รายงานทั่วไป โครงงาน รายงานวิจัย dropdown
        elem = page.locator("xpath=/html/body/div/main/div/div[3]/div[2]/div/label/select").nth(0)
        await elem.wait_for(state="visible", timeout=10000)
        await elem.select_option("")
        
        # -> Click the 'ตรวจรายงาน' button to run the analysis and then verify that the analysis results are displayed.
        # ตรวจรายงาน · ข้อมูลตัวอย่าง button
        elem = page.get_by_role('button', name='ตรวจรายงาน', exact=True)
        await elem.click(timeout=10000)
        
        # -> Click the 'ยืนยันและส่งตรวจ' (Confirm and send) button to submit the document for analysis and view the analysis results.
        # ยืนยันและส่งตรวจ button
        elem = page.get_by_role('button', name='ยืนยันและส่งตรวจ', exact=True)
        await elem.click(timeout=10000)
        
        # --> Assertions to verify final state
        
        # --> Verify the document remains available for editing
        await page.locator("xpath=/html/body/div[1]/main/div/div[2]/div/div[2]/div[1]/textarea").nth(0).scroll_into_view_if_needed()
        # Assert: The document textarea is visible and available for editing.
        await expect(page.locator("xpath=/html/body/div[1]/main/div/div[2]/div/div[2]/div[1]/textarea").nth(0)).to_be_visible(timeout=15000), "The document textarea is visible and available for editing."
        # Assert: The textarea contains the pasted document including the 'Appendix' heading, confirming the document remains editable.
        await expect(page.locator("xpath=/html/body/div[1]/main/div/div[2]/div/div[2]/div[1]/textarea").nth(0)).to_have_value("Title: The Impact of Study Habits on Academic Performance\n\nAbstract:\nThis short report examines common study habits and their correlation with academic outcomes. Methods included surveys and analysis of study schedules.\n\n1. Introduction\nEffective study habits are associated with higher performance. This report summarizes the findings from a class-wide survey.\n\n2. Methods\nA questionnaire was administered to 120 students asking about hours studied per week, preferred study environment, and use of group study.\n\n3. Results\nStudents who scheduled regular study blocks tended to report higher grades. Group study was beneficial for conceptual subjects.\n\n4. Discussion\nRecommendations include creating a weekly study plan and mixing individual and group study sessions.\n\nAppendix\nAppendix A: Survey Instrument.\nQuestion 1: How many hours per week do you study?\nQuestion 2: Where do you usually study?\n\nAppendix B: Raw Survey Responses\n- Student 1: 10 hours, library\n- Student 2: 6 hours, home ", timeout=15000), "The textarea contains the pasted document including the 'Appendix' heading, confirming the document remains editable."
        
        # --> Verify the analysis result is displayed
        # Assert: The analysis results panel is visible and shows the header 'ผลตรวจรายงานทั่วไป'.
        await expect(page.locator("xpath=/html/body/div[1]/main/div/section").nth(0)).to_contain_text("\u0e1c\u0e25\u0e15\u0e23\u0e27\u0e08\u0e23\u0e32\u0e22\u0e07\u0e32\u0e19\u0e17\u0e31\u0e48\u0e27\u0e44\u0e1b", timeout=15000), "The analysis results panel is visible and shows the header '\u0e1c\u0e25\u0e15\u0e23\u0e27\u0e08\u0e23\u0e32\u0e22\u0e07\u0e32\u0e19\u0e17\u0e31\u0e48\u0e27\u0e44\u0e1b'."
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
    