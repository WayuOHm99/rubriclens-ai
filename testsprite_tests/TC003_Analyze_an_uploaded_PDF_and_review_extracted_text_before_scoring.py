import asyncio
import re
from pathlib import Path

from playwright import async_api
from playwright.async_api import expect


async def run_test():
    fixture_path = Path(__file__).resolve().parent / "fixtures" / "sample-report.pdf"
    assert fixture_path.is_file(), "The synthetic sample PDF fixture is missing."

    async with async_api.async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 720})
        context.set_default_timeout(15000)
        page = await context.new_page()

        try:
            await page.goto("http://localhost:5173/")
            await page.locator("#pdf-upload").set_input_files(str(fixture_path))

            await expect(page.get_by_text("sample-report.pdf", exact=True)).to_be_visible()
            await expect(page.get_by_text(re.compile(r"อ่าน PDF ครบ 1 หน้าแล้ว"))).to_be_visible()

            document_text = page.locator("#report-text")
            await expect(document_text).to_have_value(re.compile(r"RubricLens Test Report"))
            await expect(document_text).to_have_value(re.compile(r"contains no personal information"))

            analyze_button = page.get_by_role("button", name=re.compile(r"^ตรวจรายงาน"))
            await expect(analyze_button).to_be_enabled()
            await analyze_button.click()

            result = page.get_by_role("region", name="ผลวิเคราะห์")
            await expect(result).to_be_visible()
            await expect(result).to_contain_text(re.compile(r"\d+%"))
        finally:
            await context.close()
            await browser.close()


asyncio.run(run_test())
