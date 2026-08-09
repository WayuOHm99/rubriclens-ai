import asyncio
import re

from playwright import async_api
from playwright.async_api import expect


REPORT = """ชื่อเรื่อง: พฤติกรรมการเรียนกับผลสัมฤทธิ์ทางการศึกษา

บทนำ
รายงานนี้ศึกษาความสัมพันธ์ระหว่างตารางทบทวนกับผลการเรียนของนักศึกษา

วิธีดำเนินการ
เก็บข้อมูลจากแบบสอบถามนักศึกษา 120 คนและเปรียบเทียบชั่วโมงทบทวนต่อสัปดาห์

ผลการศึกษา
ผู้ที่วางแผนทบทวนสม่ำเสมอรายงานว่าจดจำเนื้อหาได้ดีขึ้น

สรุป
ควรผสมผสานการอ่านรายบุคคลกับการทบทวนเป็นกลุ่ม

ภาคผนวก
แบบสอบถามและคำตอบดิบของผู้เข้าร่วม
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
            document_text = page.get_by_label("ข้อความเอกสาร")
            await document_text.fill(REPORT)

            await page.get_by_role("button", name="ตรวจรายงาน", exact=True).click()
            dialog = page.get_by_role("dialog", name="ยืนยันการไม่ส่งภาคผนวก")
            await expect(dialog).to_be_visible()
            await page.get_by_role("button", name="กลับไปแก้ข้อความ", exact=True).click()
            await expect(dialog).to_be_hidden()
            await expect(document_text).to_have_value(REPORT)

            edited_report = REPORT + "\nหมายเหตุ: ผู้เขียนตรวจทานข้อความภาคผนวกแล้ว"
            await document_text.fill(edited_report)
            await page.get_by_role("button", name="ตรวจรายงาน", exact=True).click()
            await expect(dialog).to_be_visible()
            await page.get_by_role("button", name="ยืนยันและส่งตรวจ", exact=True).click()

            result = page.get_by_role("region", name="ผลวิเคราะห์")
            await expect(result).to_be_visible()
            await expect(result).to_contain_text("ผลตรวจรายงานทั่วไป")
            await expect(document_text).to_have_value(edited_report)
            await expect(document_text).to_have_value(re.compile("ภาคผนวก"))
        finally:
            await context.close()
            await browser.close()


asyncio.run(run_test())
