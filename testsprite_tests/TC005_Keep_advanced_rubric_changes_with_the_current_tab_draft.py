import asyncio
import re

from playwright import async_api
from playwright.async_api import expect


async def run_test():
    async with async_api.async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            headless=True,
            args=["--window-size=1280,720", "--disable-dev-shm-usage", "--ipc=host", "--single-process"],
        )
        context = await browser.new_context(viewport={"width": 1280, "height": 720})
        context.set_default_timeout(15000)
        page = await context.new_page()

        try:
            await page.goto("http://localhost:5173/")
            await page.locator("#report-text").fill(
                "ร่างทดสอบในแท็บนี้มีเนื้อหาเพียงพอสำหรับยืนยันว่าเกณฑ์ที่แก้ไขจะถูกเก็บร่วมกับร่าง และเรียกคืนได้หลังโหลดหน้าใหม่"
            )

            await page.get_by_role("button", name="แก้ไขหัวข้อและน้ำหนัก", exact=True).click()
            title_input = page.get_by_label(re.compile(r"^ชื่อหัวข้อ")).first
            weight_input = page.locator('input[type="number"]').first
            await title_input.fill("บทนำและบริบท (แก้ไข)")
            await weight_input.fill("3")
            await page.get_by_role("button", name="ไม่นำมาคิดคะแนน", exact=True).first.click()

            # Draft storage is automatic; wait for the changed title to reach session storage.
            await page.wait_for_function(
                "() => sessionStorage.getItem('rubriclensai-session-draft-v1')?.includes('บทนำและบริบท (แก้ไข)')"
            )
            await page.reload()
            await expect(page.locator("#report-text")).to_have_value(re.compile(r"ร่างทดสอบในแท็บนี้"))

            await page.get_by_role("button", name="แก้ไขหัวข้อและน้ำหนัก", exact=True).click()
            await expect(page.get_by_label(re.compile(r"^ชื่อหัวข้อ")).first).to_have_value("บทนำและบริบท (แก้ไข)")
            await expect(page.locator('input[type="number"]').first).to_have_value("3")
            await expect(page.get_by_role("button", name="นำมาคิดคะแนน", exact=True).first).to_be_visible()
        finally:
            await context.close()
            await browser.close()


asyncio.run(run_test())
