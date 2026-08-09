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
        
        # -> Paste a report into the 'ข้อความเอกสาร' textarea so the app can analyze the document.
        # ข้อความเอกสาร text area
        elem = page.locator('[id="report-text"]')
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("Title: The Impact of Study Techniques on Student Learning Outcomes\n\nIntroduction:\nThis report examines the effects of various study techniques on undergraduate students' performance in a core course. The objective is to compare active recall, spaced repetition, and passive rereading to determine which technique correlates with better retention and higher assessment scores.\n\nMethods:\nA cohort of 120 students was randomly assigned to three groups. Each group practiced the same course materials over a 6-week period using one assigned technique. Pre- and post-tests were administered. Study sessions were logged, and student adherence to the assigned technique was measured through self-reports and timestamps from the learning platform.\n\nResults:\nThe active recall and spaced repetition groups showed statistically significant improvements versus the passive rereading group. Mean score improvements: active recall +15.2 points (SD 4.6), spaced repetition +13.8 points (SD 5.1), rereading +6.1 points (SD 6.3). Retention measured at 4-week follow-up remained higher for active recall.\n\nDiscussion:\nFindings indicate that active learning strategies improve both short-term and medium-term retention. Implementation suggestions include integrating low-stakes retrieval practice and scheduled review sessions into course design. Limitations include reliance on self-reported adherence and the single-course context.\n\nConclusion:\nActive recall and spaced repetition are recommended to improve student learning outcomes. Further research should test cross-disciplinary generalizability and long-term impacts.\n\nReferences:\n- Smith, J. et al. (2020) Effective Study Techniques, Journal of Learning.\n- Lee, K. (2019) Spaced Repetition in Higher Education, Education Research Quarterly.\n")
        
        # -> Open the 'ประเภทงาน' (Document type) dropdown so the matching type can be selected.
        # รายงานทั่วไป โครงงาน รายงานวิจัย dropdown
        elem = page.locator('[id="document-type"]')
        await elem.click(timeout=10000)
        
        # -> Click the 'แก้ไขหัวข้อและน้ำหนัก' (Edit topics and weights) button to open the rubric editor.
        # แก้ไขหัวข้อและน้ำหนัก button
        elem = page.get_by_role('button', name='แก้ไขหัวข้อและน้ำหนัก', exact=True)
        await elem.click(timeout=10000)
        
        # -> Click the 'ไม่นำมาคิดคะแนน' (Not counted) button for the 'บทนำและบริบท' criterion.
        # ไม่นำมาคิดคะแนน button
        elem = page.locator('xpath=/html/body/div/main/div/div[3]/div[2]/div[4]/div/div/div/button')
        await elem.click(timeout=10000)
        
        # -> Click the 'ไม่นำมาคิดคะแนน' (Not counted) button for the 'บทนำและบริบท' criterion.
        # ตรวจรายงาน · ข้อมูลตัวอย่าง button
        elem = page.get_by_role('button', name='ตรวจรายงาน', exact=True)
        await elem.click(timeout=10000)
        
        # --> Assertions to verify final state
        
        # --> Verify the analysis completes successfully
        # Assert: Analysis completed successfully and the results panel shows a score of 74%.
        await expect(page.locator("xpath=/html/body/div/main/div/section").nth(0)).to_contain_text("74%", timeout=15000), "Analysis completed successfully and the results panel shows a score of 74%."
        
        # --> Verify criterion-level feedback reflects the not applicable adjustment
        # Assert: The results panel indicates that unrelated topics are not counted ('หัวข้อที่ไม่เกี่ยวข้องไม่ถูกนับ').
        await expect(page.locator("xpath=/html/body/div/main/div/section").nth(0)).to_contain_text("\u0e2b\u0e31\u0e27\u0e02\u0e49\u0e2d\u0e17\u0e35\u0e48\u0e44\u0e21\u0e48\u0e40\u0e01\u0e35\u0e48\u0e22\u0e27\u0e02\u0e49\u0e2d\u0e07\u0e44\u0e21\u0e48\u0e16\u0e39\u0e01\u0e19\u0e31\u0e1a", timeout=15000), "The results panel indicates that unrelated topics are not counted ('\u0e2b\u0e31\u0e27\u0e02\u0e49\u0e2d\u0e17\u0e35\u0e48\u0e44\u0e21\u0e48\u0e40\u0e01\u0e35\u0e48\u0e22\u0e27\u0e02\u0e49\u0e2d\u0e07\u0e44\u0e21\u0e48\u0e16\u0e39\u0e01\u0e19\u0e31\u0e1a')."
        # Assert: The rubric shows the criterion named 'บทนำและบริบท', confirming which criterion was adjusted.
        await expect(page.locator("xpath=/html/body/div/main/div/div[3]/div[2]/div[4]/div[1]/div/label[1]/input").nth(0)).to_have_value("\u0e1a\u0e17\u0e19\u0e33\u0e41\u0e25\u0e30\u0e1a\u0e23\u0e34\u0e1a\u0e17", timeout=15000), "The rubric shows the criterion named '\u0e1a\u0e17\u0e19\u0e33\u0e41\u0e25\u0e30\u0e1a\u0e23\u0e34\u0e1a\u0e17', confirming which criterion was adjusted."
        await asyncio.sleep(5)

    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if pw:
            await pw.stop()

asyncio.run(run_test())
    