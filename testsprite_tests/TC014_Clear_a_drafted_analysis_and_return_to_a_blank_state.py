import asyncio

from playwright import async_api
from playwright.async_api import expect


async def run_test():
    async with async_api.async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 720})
        context.set_default_timeout(15000)
        page = await context.new_page()

        try:
            await page.goto("http://localhost:5173/")
            document_text = page.locator("#report-text")
            await document_text.fill("ร่างรายงานสังเคราะห์สำหรับยืนยันว่าปุ่มเริ่มใหม่ล้างข้อมูลในแท็บได้จริง")
            await page.wait_for_timeout(400)

            page.once("dialog", lambda dialog: asyncio.create_task(dialog.accept()))
            await page.get_by_role("button", name="เริ่มใหม่", exact=True).click()

            await expect(document_text).to_have_value("")
            await expect(page.get_by_role("button", name="เริ่มใหม่", exact=True)).to_have_count(0)
            stored_drafts = await page.evaluate(
                """() => ({
                    current: sessionStorage.getItem('rubriclensai-session-draft-v1'),
                    legacy: sessionStorage.getItem('rubriclens-session-draft-v1')
                })"""
            )
            assert stored_drafts == {"current": None, "legacy": None}, "Start over did not remove the session draft."
        finally:
            await context.close()
            await browser.close()


asyncio.run(run_test())
