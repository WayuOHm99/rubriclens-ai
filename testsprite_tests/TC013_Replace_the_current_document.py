import asyncio

from playwright import async_api
from playwright.async_api import expect


async def run_test():
    async with async_api.async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            headless=True,
            args=["--disable-dev-shm-usage"],
        )
        context = await browser.new_context(viewport={"width": 1280, "height": 720})
        context.set_default_timeout(15000)
        page = await context.new_page()

        try:
            await page.goto("http://localhost:5173/", wait_until="domcontentloaded")
            document_text = page.get_by_label("ข้อความเอกสาร")
            await document_text.fill("รายงานฉบับเดิมที่ผู้ใช้ต้องการแทนที่ด้วยเอกสารฉบับใหม่")

            page.once("dialog", lambda dialog: asyncio.create_task(dialog.accept()))
            await page.get_by_role("button", name="เริ่มใหม่", exact=True).click()
            await expect(document_text).to_have_value("")

            replacement = "รายงานฉบับใหม่มีบทนำ วิธีดำเนินงาน ผลลัพธ์ และสรุปครบถ้วนสำหรับเริ่มตรวจอีกครั้ง"
            await document_text.fill(replacement)
            await expect(document_text).to_have_value(replacement)
            await expect(page.get_by_role("button", name="ตรวจรายงาน", exact=True)).to_be_enabled()
        finally:
            await context.close()
            await browser.close()


asyncio.run(run_test())
