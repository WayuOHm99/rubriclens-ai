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
            analyze_button = page.get_by_role("button", name="ตรวจรายงาน", exact=True)

            await expect(analyze_button).to_be_disabled()
            await expect(page.get_by_text("วางข้อความหรือเลือก PDF ก่อน ปุ่มนี้จึงจะกดได้", exact=True)).to_be_visible()

            await page.get_by_label("ข้อความเอกสาร").fill(
                "รายงานนี้สรุปผลกระทบของการเติบโตของเมืองต่อระบบนิเวศ โดยทบทวนงานวิจัย เปรียบเทียบข้อมูล และเสนอให้เพิ่มพื้นที่สีเขียวพร้อมระบบติดตามผล"
            )
            await expect(analyze_button).to_be_enabled()
            await analyze_button.click()

            result = page.get_by_role("region", name="ผลวิเคราะห์")
            await expect(result).to_be_visible()
            await expect(result).to_contain_text("ผลตรวจรายงานทั่วไป")
            await expect(result).to_contain_text("ผลจากข้อมูลตัวอย่างในเบราว์เซอร์")
        finally:
            await context.close()
            await browser.close()


asyncio.run(run_test())
