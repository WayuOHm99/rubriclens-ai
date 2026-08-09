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
            await page.get_by_role("button", name="แก้ไขหัวข้อและน้ำหนัก", exact=True).click()
            await expect(page.get_by_text("ใช้ 8/8 หัวข้อ", exact=True)).to_be_visible()

            await page.get_by_role("button", name="เพิ่มหัวข้อใหม่", exact=True).click()
            await expect(page.get_by_text("ใช้ 9/9 หัวข้อ", exact=True)).to_be_visible()
            await expect(page.get_by_label("ชื่อหัวข้อ หัวข้อใหม่")).to_be_visible()

            page.once("dialog", lambda dialog: asyncio.create_task(dialog.accept()))
            await page.get_by_role("button", name="ลบ หัวข้อใหม่", exact=True).click()

            await expect(page.get_by_text("ใช้ 8/8 หัวข้อ", exact=True)).to_be_visible()
            await expect(page.get_by_label("ชื่อหัวข้อ หัวข้อใหม่")).to_have_count(0)
            await expect(page.get_by_label("ชื่อหัวข้อ บทนำและบริบท")).to_be_visible()
        finally:
            await context.close()
            await browser.close()


asyncio.run(run_test())
