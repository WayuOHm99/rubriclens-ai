import { describe, expect, it } from 'vitest'

import config from './playwright.config'

describe('E2E evidence guard', () => {
  it('ไม่ยอมให้ Playwright รันเฉพาะ test ที่ติด .only แม้รันในเครื่อง', () => {
    expect(config.forbidOnly).toBe(true)
  })
})
