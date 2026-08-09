import asyncio
import base64
import re

from playwright import async_api
from playwright.async_api import expect


MULTI_COLUMN_PDF_BASE64 = "JVBERi0xLjcKJYGBgYEKCjcgMCBvYmoKPDwKL0ZpbHRlciAvRmxhdGVEZWNvZGUKL0xlbmd0aCA1MzcKPj4Kc3RyZWFtCnictZfditUwEMfv+xS5FnadmcxXQAT3nC5eeCP0BUR3RVmRFfH5nfTQ41ez5AihUNpJwvznN5Np+jjdLBNcgye4Rokbefr2cXr++u7hx933T+/fXd18ffhwZVCcHcxLQk/L/UScljcTJogLE3sy17R8mV7w0UQPxlroqFlv41n0qDMBi7mxkaLmOh5j1apaVrvEiLxMy+dpeTbNy/R2ely1rS52JBVjUidRT5j3JTGfJB1UVGM6/C7oAlcEAA5SIsQ9V5ng7EsoAjP1//NWTKCSA0sI+zHhUzHF2yH8zyoEGfOreBcLwMoxe46ZYQ/8s27r5kjEmhbqVFjTJDlrRbGjcEWBT6P4V2TNvOVT3fwSWK3rumNcVT4rnuumU66zADpgG6h6N1AaAdQ16srQzZtAN4ldQGksUHGKHUs578utQKUbaB4BFKNRCTGatIHKBUDzWKDm7gUx/DeBUjdQHgG0WMnMhUqbJ13Ak8fyJAPHUorsN6jgKaWbp4zgqQbRP0mVm0A3iV1AZXCBZhEt7M0OKtrNU4d0UHMGFENs89QLeOpYnkXVo6lwaW54yd1AbQRQkthCcTJ7oj7zBTxtLE8kk0zkmZo8oZunDzkzGUFknUr7i7RJ7ALqY4GuR16WqAIj06CKu1Q5wyb5xEtqnOHMV2J/HvblLA6V10Birt6GpbKkeK5julo23hihFcvxe5D/kv4TMRXJzwplbmRzdHJlYW0KZW5kb2JqCgo4IDAgb2JqCjw8Ci9GaWx0ZXIgL0ZsYXRlRGVjb2RlCi9UeXBlIC9PYmpTdG0KL04gNgovRmlyc3QgMzIKL0xlbmd0aCA1NDAKPj4Kc3RyZWFtCnic1VTbitswEH33V+ixfVg0Gt1GJQRybaEsXXYLLS198MYiuASrJErZ/n1HdrZlEy8tfStmsKVz5mYdjRIgUBgjtPAkjLAahRVOGeGEByUmk0q+//EtCnlTb+Ohkm/b5iA+MwriVnyp5CIduyxUNZ1Wv7mLOte7tK0GJ6EK+ZFxs0/NcRP3YrJerdcAHgCcYXMAuOT3gi2wIa8ZQ+JvNm9OxnteA+gZY+vBnB98Ct5z7cl/xW/musJZDlxDw/pX3pJrNcTAP9UTppW8Ts2yzlG8WL5CQAcEQRkTjPv0kn/HPtY5/b/N9fW3qXu2wyfnvE5druTd8T73y7KpKjmvD7EgQr6Ju+8xt5u6kqtuk5q22wr5oe1m3aF93PjHiFfztGv+OmzRYVHjPhax9nKUt/GQjvsN67Pw+vDl42mGKw+B+K96Cnwver8zQvAGHaF19AyhnDOBDeQuCYEP07iA4PnunWHeerRaO/a7wMhYUARqzI8c5/KK+vt8hllC4xxqPYIp7tOiUd6O1EJEQSnW2yUWfNCsDgyXEHogFUKwIy2wJLk3dM6MpNPWumBorDtPBpT1So1U4hxprU0YqRItl4JgRrIp9Dz2kHj0XVbiETgshpGf0p+usRzZo3d4Ol3Wnfz47v5r3PR6KsvVQ359l8uNGjbK3nVs2nqeHniWAj+WE5DBMlFnXZdymbH9dO0yS7as/GnisvNP5OlxSAplbmRzdHJlYW0KZW5kb2JqCgo5IDAgb2JqCjw8Ci9TaXplIDEwCi9Sb290IDIgMCBSCi9JbmZvIDMgMCBSCi9GaWx0ZXIgL0ZsYXRlRGVjb2RlCi9UeXBlIC9YUmVmCi9MZW5ndGggNDIKL1cgWyAxIDIgMiBdCj4+CnN0cmVhbQp4nBXJsQ0AMAgEsYMQKSWTZR62B75xY6DbeSBMuDgixDWSnb9EwQBqTwMpCmVuZHN0cmVhbQplbmRvYmoKCnN0YXJ0eHJlZgoxMjY4CiUlRU9G"


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
            await page.locator("#pdf-upload").set_input_files(
                {
                    "name": "multi-column-report.pdf",
                    "mimeType": "application/pdf",
                    "buffer": base64.b64decode(MULTI_COLUMN_PDF_BASE64),
                }
            )

            await expect(page.get_by_text("multi-column-report.pdf", exact=True)).to_be_visible()
            await expect(page.get_by_text(re.compile(r"อ่าน PDF ครบ 1 หน้าแล้ว"))).to_be_visible()
            await expect(page.get_by_text(re.compile(r"อาจมีหลายคอลัมน์"))).to_be_visible()

            document_text = page.get_by_label("ข้อความเอกสาร")
            await expect(document_text).to_have_value(re.compile(r"Left column 1"))
            await expect(document_text).to_have_value(re.compile(r"Right column 1"))
            await expect(page.get_by_role("button", name="ตรวจรายงาน", exact=True)).to_be_enabled()
        finally:
            await context.close()
            await browser.close()


asyncio.run(run_test())
