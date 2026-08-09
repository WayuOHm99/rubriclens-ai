import { expect, test } from '@playwright/test'

/**
 * หน้ากฎหมายถูก build เป็นไฟล์ HTML แยกของตัวเอง (ไม่ใช่ SPA route)
 * ชุดนี้จึงตรวจสิ่งที่เทสต์ระดับ component ตรวจแทนไม่ได้ คือ URL จริงเปิดได้
 * และการเดินจากหน้าแรกไปหน้ากฎหมายด้วยการคลิกจริงบนบันเดิลที่จะ deploy
 */

test('ผู้ใช้เดินจากหน้าแรกไปหน้านโยบายความเป็นส่วนตัวด้วยลิงก์ท้ายเว็บได้', async ({ page }) => {
  await page.goto('/')

  await page.getByRole('contentinfo').getByRole('link', { name: 'นโยบายความเป็นส่วนตัว' }).click()

  await expect(page).toHaveURL(/\/privacy(\.html)?$/)
  await expect(page.getByRole('heading', { name: 'นโยบายความเป็นส่วนตัว', level: 1 })).toBeVisible()
})

test('ผู้ใช้เดินจากหน้าแรกไปหน้าข้อกำหนดการใช้งานด้วยลิงก์ท้ายเว็บได้', async ({ page }) => {
  await page.goto('/')

  await page.getByRole('contentinfo').getByRole('link', { name: 'ข้อกำหนดการใช้งาน' }).click()

  await expect(page).toHaveURL(/\/terms(\.html)?$/)
  await expect(page.getByRole('heading', { name: 'ข้อกำหนดการใช้งาน', level: 1 })).toBeVisible()
})

test('หน้านโยบายเปิดตรงจาก URL ได้ และกลับหน้าตรวจเอกสารได้', async ({ page }) => {
  await page.goto('/privacy')

  await expect(page.getByRole('heading', { name: '7. คุกกี้และที่เก็บข้อมูลในเบราว์เซอร์' })).toBeVisible()

  await page.getByRole('link', { name: '← กลับไปหน้าตรวจเอกสาร' }).click()
  await expect(page.getByRole('heading', { name: 'RubricLensAi', level: 1 })).toBeVisible()
})

test('ผู้ใช้คีย์บอร์ดเลื่อนอ่านตารางนโยบายบนจอแคบได้', async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 800 })
  await page.goto('/privacy')

  const tableRegion = page.getByRole('region', { name: 'ตารางข้อมูลชั่วคราวบนเซิร์ฟเวอร์' })
  await tableRegion.focus()
  await expect(tableRegion).toBeFocused()
  const before = await tableRegion.evaluate((element) => element.scrollLeft)
  await tableRegion.press('ArrowRight')
  await expect.poll(() => tableRegion.evaluate((element) => element.scrollLeft)).toBeGreaterThan(before)

  const backLink = page.getByRole('link', { name: '← กลับไปหน้าตรวจเอกสาร' })
  expect((await backLink.boundingBox())?.height ?? 0).toBeGreaterThanOrEqual(44)
})

test('หน้ากฎหมายไม่เขียนอะไรลงที่เก็บข้อมูลของเบราว์เซอร์', async ({ page }) => {
  await page.goto('/terms')

  const storageCounts = await page.evaluate(() => ({
    local: window.localStorage.length,
    session: window.sessionStorage.length,
  }))

  expect(storageCounts).toEqual({ local: 0, session: 0 })
})
