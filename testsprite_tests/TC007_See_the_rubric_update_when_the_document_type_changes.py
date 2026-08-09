import asyncio

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
            await page.goto("http://localhost:5173/", wait_until="domcontentloaded")

            document_type = page.get_by_label("ประเภทงาน")
            await expect(document_type).to_have_value("general-report")
            await expect(page.get_by_text("ใช้ 8/8 หัวข้อ", exact=True)).to_be_visible()

            await document_type.select_option("project")

            await expect(document_type).to_have_value("project")
            await expect(page.get_by_label("ชุดเกณฑ์การตรวจ")).to_have_value("project-th-v1")
            await expect(page.get_by_text("ใช้ 10/10 หัวข้อ", exact=True)).to_be_visible()
            await expect(page.get_by_text("จุดเน้น:", exact=True)).to_be_visible()
            await expect(page.get_by_text("ข้อจำกัด:", exact=True)).to_be_visible()
            await expect(page.get_by_text("ไม่สามารถยืนยันว่าได้ลงมือทำหรือทดสอบจริง")).to_be_visible()
            await expect(page.get_by_role("button", name="ตรวจโครงงาน", exact=True)).to_be_visible()
        finally:
            await context.close()
            await browser.close()


asyncio.run(run_test())
