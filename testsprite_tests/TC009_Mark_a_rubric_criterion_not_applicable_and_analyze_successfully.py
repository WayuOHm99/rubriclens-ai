import asyncio

from playwright import async_api
from playwright.async_api import expect


REPORT = """หัวข้อ: เทคนิคการเรียนกับผลสัมฤทธิ์ของนักศึกษา

บทนำ
รายงานนี้เปรียบเทียบการทบทวนแบบเว้นระยะกับการอ่านซ้ำ

วิธีดำเนินการ
นักศึกษา 120 คนบันทึกเวลาเรียนและทำแบบทดสอบก่อนกับหลังการทดลอง

ผลการศึกษา
กลุ่มที่ทบทวนแบบเว้นระยะมีคะแนนหลังเรียนสูงขึ้นอย่างชัดเจน

สรุป
การวางแผนทบทวนอย่างสม่ำเสมอช่วยให้จดจำเนื้อหาได้นานขึ้น
"""


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
            await page.get_by_label("ข้อความเอกสาร").fill(REPORT)
            await page.get_by_role("button", name="แก้ไขหัวข้อและน้ำหนัก", exact=True).click()

            not_counted_buttons = page.get_by_role("button", name="ไม่นำมาคิดคะแนน", exact=True)
            await expect(not_counted_buttons).to_have_count(8)
            await not_counted_buttons.first.click()

            await expect(page.get_by_text("ใช้ 7/8 หัวข้อ", exact=True)).to_be_visible()
            await expect(page.get_by_role("button", name="นำมาคิดคะแนน", exact=True).first).to_be_visible()

            await page.get_by_role("button", name="ตรวจรายงาน", exact=True).click()
            result = page.get_by_role("region", name="ผลวิเคราะห์")
            await expect(result).to_be_visible()
            await expect(result).to_contain_text("ผลตรวจรายงานทั่วไป")
            await expect(result).to_contain_text("ใช้ประเมิน 7/7 หัวข้อ")
            await expect(result.get_by_text("บทนำและบริบท", exact=True)).to_have_count(0)
        finally:
            await context.close()
            await browser.close()


asyncio.run(run_test())
