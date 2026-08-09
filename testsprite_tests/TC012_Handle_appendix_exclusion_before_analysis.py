import asyncio

from playwright import async_api
from playwright.async_api import expect


REPORT = """บทนำ
รายงานนี้อธิบายผลการสำรวจพฤติกรรมการอ่านของนักศึกษาและสรุปข้อเสนอแนะจากข้อมูล

ผลการสำรวจ
ผู้ตอบส่วนใหญ่อ่านหนังสือในช่วงเย็นและต้องการพื้นที่ที่เงียบ

สรุป
ห้องสมุดควรเพิ่มพื้นที่อ่านแบบเงียบในช่วงสอบ

ภาคผนวก ก
แบบสอบถามฉบับเต็มและข้อมูลดิบที่ไม่ต้องส่งไปวิเคราะห์
"""


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
            document_text = page.get_by_label("ข้อความเอกสาร")
            await document_text.fill(REPORT)
            await page.get_by_role("button", name="ตรวจรายงาน", exact=True).click()

            dialog = page.get_by_role("dialog", name="ยืนยันการไม่ส่งภาคผนวก")
            await expect(dialog).to_be_visible()
            await expect(dialog).to_contain_text("ระบบจะไม่นำส่วนนี้ไปวิเคราะห์")
            await page.get_by_role("button", name="ยืนยันและส่งตรวจ", exact=True).click()

            result = page.get_by_role("region", name="ผลวิเคราะห์")
            await expect(result).to_be_visible()
            await expect(result).to_contain_text("ผลตรวจรายงานทั่วไป")
            await expect(document_text).to_have_value(REPORT)
            await expect(dialog).to_be_hidden()
        finally:
            await context.close()
            await browser.close()


asyncio.run(run_test())
