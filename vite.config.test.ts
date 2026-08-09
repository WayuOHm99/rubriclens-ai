import { readFileSync } from 'node:fs'
import path from 'node:path'

import { describe, expect, it } from 'vitest'

import config from './vite.config'

describe('local Worker connection', () => {
  it('ส่งคำขอ /api จาก Vite ไปยัง Worker ที่รันในเครื่อง', () => {
    if (typeof config === 'function') throw new Error('Expected a static Vite configuration')

    expect(config.server?.proxy?.['/api']).toMatchObject({
      target: 'http://127.0.0.1:8787',
      changeOrigin: true,
    })
  })
})

describe('test evidence guard', () => {
  it('ไม่ยอมให้ Vitest รันเฉพาะ test ที่ติด .only แม้รันในเครื่อง', () => {
    if (typeof config === 'function') throw new Error('Expected a static Vite configuration')

    expect(config.test?.allowOnly).toBe(false)
  })
})

describe('favicon shown in the browser tab', () => {
  it('ทุกหน้าขอไอคอน RubricLensAi รุ่นใหม่แทนไอคอนเก่าที่เบราว์เซอร์จำไว้', () => {
    const pages = ['index.html', 'privacy.html', 'terms.html', 'public/404.html']

    for (const page of pages) {
      const html = readFileSync(path.resolve(import.meta.dirname, page), 'utf8')
      expect(html, page).toContain('href="/favicon.svg?v=rubriclens-1"')
    }
  })
})
