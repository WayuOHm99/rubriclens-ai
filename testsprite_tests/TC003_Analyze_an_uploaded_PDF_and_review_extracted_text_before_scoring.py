import asyncio
import base64
import re

from playwright import async_api
from playwright.async_api import expect


SAMPLE_PDF_BASE64 = "JVBERi0xLjcKJYGBgYEKCjcgMCBvYmoKPDwKL0ZpbHRlciAvRmxhdGVEZWNvZGUKL0xlbmd0aCA1MDEKPj4Kc3RyZWFtCnicpZTdbhQxDIXv8xS5RmpJHMd2pIqLbmfFBTdI8wIICgK1QkWI5+fEmdndwg7aCq1mZ/Iz43M+23kKt3NI18lius4Vf2Txx5fw+u39w6/7n18/fri6/f7w6UpTM7ak1iKlOH8OxHF+F3JM+OXIFtUkzo/hppJWISVpUngnVSYtlCpL1aKMJ8JTkr2S8ps4fwvzqzDN4X14ciX+wTMCGt4VoyoWM58XwOQCuCEkQ8BeGFIQFFL2Ml0WjFJKlmqDm5zPx8k2jLKYtG4OxjwmxtWj9bkTmxgJRh2J4KoOJDGzYKWDsb5n3LErHzVjNsskfZUxLvBz50h5WcmyU2hwHRc6XHBCgDTE38IpOvLJd27KHGe5LITCbC1FtiFKpSPE+hcuIBqYJI81GGVcJDvffYS2k6wdKZ2gKh2d9v1tVB/m93irIyb11Q4O81hHShAVWPMB+ktAGteULeV/gMxpaQxvgYqMXQwSbJqh4NS2QNa17RaQf1RRfQZkrZzSUeFOB/SjLnXZ34EPLAP2SNFICi1vZDjxlh5p+o9arEYsQqVstnZlHrU4clcQqIt5QVtnnF6VGKI3QdJIE2dvaBwc4jWIONKT1m3jPnkrwqIutXeo0g6voWtsxa4nCXdE4nVLR6TrIbAcI8kPrTVq/8Zzd78B6RU9rQplbmRzdHJlYW0KZW5kb2JqCgo4IDAgb2JqCjw8Ci9GaWx0ZXIgL0ZsYXRlRGVjb2RlCi9UeXBlIC9PYmpTdG0KL04gNgovRmlyc3QgMzIKL0xlbmd0aCA0NTIKPj4Kc3RyZWFtCnic1VTda9wwDH/3X6HH7aFYdvw5joP7SDYYZaUdbGzsIU3MkXHY4+Ib3X8/Obl2dL2ysbcRRCzp95NsWZYABAlKQQXWgQJdSdBghAIDFgUsFoy///EtAL9qd2Fk/O3Qj/CZvAjX8IXxTTrGDIItl+wXdtPmdp92bCaBKOB7xNUh9ccuHGDR1E2DaBHRKBKDKLf035B4Ekk6+aSjNYlVJyGbrRCrFfmaWYydOcU/YfWJX9OfsKZgtjNWuVl/yFty1XMM+af9+CXjl6nftjnAi+0ridKgQy+U8sp8eknlOIQ2p//3cNP+hxSfPeGje25SzIzfHG/zpBajYHzdjqF4gL8J++8hD13LeB271A9xB/zDEFdxHO4N/xjxYp32/V+HLX1YuvEQSrNO7civw5iOh476s+Cm8GXxOMOFRe+oqtZ5ehcT7zeAt0oaJ7VxTwHlih1q7ww9rfNkjcp4ifYp2WordVWZZ8lOaRQOxTmyM5TVCjc96nNk7aQyRlbVmW0LOrGWSlh9IlMt+cd3t19DN9WoqPVdfn2TS5fMhmK7DP3QrtMdzQekT3sNTskyJVYxplzmxjQxYqZrKJo9TREi/wSwLSUpCmVuZHN0cmVhbQplbmRvYmoKCjkgMCBvYmoKPDwKL1NpemUgMTAKL1Jvb3QgMiAwIFIKL0luZm8gMyAwIFIKL0ZpbHRlciAvRmxhdGVEZWNvZGUKL1R5cGUgL1hSZWYKL0xlbmd0aCA0MwovVyBbIDEgMiAyIF0KL0luZGV4IFsgMCAxMCBdCj4+CnN0cmVhbQp4nBXJsQ0AMAgEsYMQKSWTZR62B75xY6DbeSBMuDgixDWSnb9EwQBqTwMpCmVuZHN0cmVhbQplbmRvYmoKCnN0YXJ0eHJlZgoxMTQ0CiUlRU9G"


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
            await page.locator("#pdf-upload").set_input_files(
                {
                    "name": "sample-report.pdf",
                    "mimeType": "application/pdf",
                    "buffer": base64.b64decode(SAMPLE_PDF_BASE64),
                }
            )

            await expect(page.get_by_text("sample-report.pdf", exact=True)).to_be_visible()
            await expect(page.get_by_text(re.compile(r"อ่าน PDF ครบ 1 หน้าแล้ว"))).to_be_visible()

            document_text = page.get_by_label("ข้อความเอกสาร")
            await expect(document_text).to_have_value(re.compile(r"RubricLens Test Report"))
            await expect(document_text).to_have_value(re.compile(r"contains no personal information"))

            analyze_button = page.get_by_role("button", name="ตรวจรายงาน", exact=True)
            await expect(analyze_button).to_be_enabled()
            await analyze_button.click()

            result = page.get_by_role("region", name="ผลวิเคราะห์")
            await expect(result).to_be_visible()
            await expect(result).to_contain_text("ผลตรวจรายงานทั่วไป")
            await expect(result).to_contain_text(re.compile(r"\d+%"))
        finally:
            await context.close()
            await browser.close()


asyncio.run(run_test())
