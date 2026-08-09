import { beforeEach, describe, expect, it, vi } from 'vitest'

const pdfMocks = vi.hoisted(() => ({
  getDocument: vi.fn(),
  destroy: vi.fn(),
  getPage: vi.fn(),
}))

vi.mock('pdfjs-dist/build/pdf.worker.min.mjs?url', () => ({ default: 'blob:pdf-worker' }))
vi.mock('pdfjs-dist', () => ({
  getDocument: pdfMocks.getDocument,
  GlobalWorkerOptions: { workerSrc: '' },
}))

import { MAX_PDF_PAGES, MAX_RAW_CHARS } from './document'
import { extractPdfText } from './pdf'

/** A File whose bytes start with a valid PDF signature; page count comes from the mock. */
function fakePdfFile() {
  return new File([new TextEncoder().encode('%PDF-1.7 stub')], 'report.pdf', { type: 'application/pdf' })
}

function mockPdfWithPages(numPages: number) {
  pdfMocks.getPage.mockImplementation(() => Promise.resolve({
    getTextContent: () => Promise.resolve({ items: [{ str: 'เนื้อหา', transform: [1, 0, 0, 1, 48, 700] }] }),
    getViewport: () => ({ width: 595 }),
  }))
  pdfMocks.getDocument.mockReturnValue({
    promise: Promise.resolve({ numPages, getPage: pdfMocks.getPage }),
    destroy: pdfMocks.destroy,
  })
}

function mockPdfWithTextItems(pages: Array<Array<{ str: string; transform: number[] }>>) {
  pdfMocks.getPage.mockImplementation((pageNumber: number) => Promise.resolve({
    getTextContent: () => Promise.resolve({ items: pages[pageNumber - 1] }),
    getViewport: () => ({ width: 595 }),
  }))
  pdfMocks.getDocument.mockReturnValue({
    promise: Promise.resolve({ numPages: pages.length, getPage: pdfMocks.getPage }),
    destroy: pdfMocks.destroy,
  })
}

describe('extractPdfText', () => {
  beforeEach(() => {
    pdfMocks.getDocument.mockReset()
    pdfMocks.destroy.mockReset()
    pdfMocks.getPage.mockReset()
  })

  it('rejects a PDF over the page limit before extracting any page', async () => {
    mockPdfWithPages(MAX_PDF_PAGES + 1)

    await expect(extractPdfText(fakePdfFile())).rejects.toThrow(new RegExp(`${MAX_PDF_PAGES.toLocaleString()} หน้า`))
    expect(pdfMocks.getPage).not.toHaveBeenCalled()
  })

  it('still releases the pdf.js loading task when the page limit stops extraction', async () => {
    mockPdfWithPages(MAX_PDF_PAGES + 500)

    await expect(extractPdfText(fakePdfFile())).rejects.toThrow()
    expect(pdfMocks.destroy).toHaveBeenCalledTimes(1)
  })

  it('extracts a document that sits exactly on the limit', async () => {
    mockPdfWithPages(MAX_PDF_PAGES)
    const progress = vi.fn()

    const extraction = await extractPdfText(fakePdfFile(), { onProgress: progress })

    expect(extraction.pageCount).toBe(MAX_PDF_PAGES)
    expect(pdfMocks.getPage).toHaveBeenCalledTimes(MAX_PDF_PAGES)
    expect(progress).toHaveBeenLastCalledWith(MAX_PDF_PAGES, MAX_PDF_PAGES)
  })

  it('rejects a file that is not a PDF before opening it', async () => {
    const notPdf = new File([new TextEncoder().encode('hello world')], 'notes.pdf', { type: 'application/pdf' })
    await expect(extractPdfText(notPdf)).rejects.toThrow('ไฟล์ไม่มีโครงสร้าง PDF ที่ถูกต้อง')
    expect(pdfMocks.getDocument).not.toHaveBeenCalled()
  })

  it('stops before opening the document when the caller already aborted', async () => {
    const controller = new AbortController()
    controller.abort()
    await expect(extractPdfText(fakePdfFile(), { signal: controller.signal })).rejects.toThrow('ยกเลิกการอ่าน PDF')
    expect(pdfMocks.getDocument).not.toHaveBeenCalled()
  })

  it('stops reading later pages as soon as extracted text exceeds the running character limit', async () => {
    mockPdfWithTextItems([
      [{ str: 'ก'.repeat(200_000), transform: [1, 0, 0, 1, 48, 700] }],
      [{ str: 'ข'.repeat(100_000), transform: [1, 0, 0, 1, 48, 700] }],
      [{ str: 'หน้านี้ต้องไม่ถูกอ่าน', transform: [1, 0, 0, 1, 48, 700] }],
    ])

    await expect(extractPdfText(fakePdfFile())).rejects.toThrow(MAX_RAW_CHARS.toLocaleString())
    expect(pdfMocks.getPage).toHaveBeenCalledTimes(2)
    expect(pdfMocks.destroy).toHaveBeenCalledTimes(1)
  })

  it('accepts extracted text exactly at the running character limit', async () => {
    mockPdfWithTextItems([[
      { str: 'ก'.repeat(MAX_RAW_CHARS), transform: [1, 0, 0, 1, 48, 700] },
    ]])

    const extraction = await extractPdfText(fakePdfFile())

    expect(extraction.text).toHaveLength(MAX_RAW_CHARS)
  })

  it('stops reading later pages when PDF text-item work exceeds the running item limit', async () => {
    const blankItem = { str: ' ', transform: [1, 0, 0, 1, 48, 700] }
    const itemsPerPage = Math.floor(MAX_RAW_CHARS / 2) + 1
    mockPdfWithTextItems([
      new Array(itemsPerPage).fill(blankItem),
      new Array(itemsPerPage).fill(blankItem),
      [{ str: 'หน้านี้ต้องไม่ถูกอ่าน', transform: [1, 0, 0, 1, 48, 700] }],
    ])

    await expect(extractPdfText(fakePdfFile())).rejects.toThrow(`${MAX_RAW_CHARS.toLocaleString()} รายการ`)
    expect(pdfMocks.getPage).toHaveBeenCalledTimes(2)
    expect(pdfMocks.destroy).toHaveBeenCalledTimes(1)
  })

  it('accepts exactly the maximum number of PDF text items', async () => {
    const blankItem = { str: ' ', transform: [1, 0, 0, 1, 48, 700] }
    mockPdfWithTextItems([new Array(MAX_RAW_CHARS).fill(blankItem)])

    const extraction = await extractPdfText(fakePdfFile())

    expect(extraction.text).toBe('')
    expect(pdfMocks.getPage).toHaveBeenCalledTimes(1)
  })

  it('groups many separate text lines with work that grows linearly instead of comparing every line pair', async () => {
    const itemCount = 80
    mockPdfWithTextItems([Array.from({ length: itemCount }, (_, index) => ({
      str: `บรรทัด-${index}`,
      transform: [1, 0, 0, 1, 48, index * 10],
    }))])
    const absoluteValue = vi.spyOn(Math, 'abs')

    let extraction: Awaited<ReturnType<typeof extractPdfText>>
    let comparisonCount = 0
    try {
      extraction = await extractPdfText(fakePdfFile())
      comparisonCount = absoluteValue.mock.calls.length
    } finally {
      absoluteValue.mockRestore()
    }

    expect(extraction.text.split('\n')).toEqual(
      Array.from({ length: itemCount }, (_, index) => `บรรทัด-${itemCount - index - 1}`),
    )
    expect(comparisonCount).toBeLessThan(itemCount * 4)
  })

  it('sorts each detected line once instead of sorting again for every added text item', async () => {
    const itemCount = 40
    mockPdfWithTextItems([Array.from({ length: itemCount }, (_, index) => ({
      str: `คำ-${index}`,
      transform: [1, 0, 0, 1, itemCount - index, 700],
    }))])
    const sort = vi.spyOn(Array.prototype, 'sort')

    let extraction: Awaited<ReturnType<typeof extractPdfText>>
    let sortCount = 0
    try {
      extraction = await extractPdfText(fakePdfFile())
      sortCount = sort.mock.calls.length
    } finally {
      sort.mockRestore()
    }

    expect(extraction.text).toBe(Array.from({ length: itemCount }, (_, index) => `คำ-${itemCount - index - 1}`).join(' '))
    expect(sortCount).toBeLessThanOrEqual(4)
  })

  it('keeps first-created-line grouping when one item is close enough to two lines', async () => {
    mockPdfWithTextItems([[
      { str: 'ล่าง', transform: [1, 0, 0, 1, 10, 0] },
      { str: 'บน', transform: [1, 0, 0, 1, 10, 6] },
      { str: 'กึ่งกลาง', transform: [1, 0, 0, 1, 20, 3] },
    ]])

    const extraction = await extractPdfText(fakePdfFile())

    expect(extraction.text).toBe('บน\nล่าง กึ่งกลาง')
  })

  it('keeps text cleanup and multi-column warnings unchanged after bounded processing', async () => {
    mockPdfWithTextItems([[
      { str: 'ก\u0001', transform: [1, 0, 0, 1, 0, 30] },
      { str: 'ข', transform: [1, 0, 0, 1, 200, 30] },
      { str: 'ค', transform: [1, 0, 0, 1, 0, 20] },
      { str: 'ง', transform: [1, 0, 0, 1, 200, 20] },
      { str: 'จ', transform: [1, 0, 0, 1, 0, 10] },
      { str: 'ฉ', transform: [1, 0, 0, 1, 200, 10] },
    ]])

    const extraction = await extractPdfText(fakePdfFile())

    expect(extraction.text).toBe('ก ข\nค ง\nจ ฉ')
    expect(extraction.warnings).toContain('พบและนำอักขระควบคุมที่มองไม่เห็นออกจากข้อความ โปรดตรวจคำภาษาไทยและสระวรรณยุกต์ก่อนยืนยัน')
    expect(extraction.warnings).toContain('ตรวจพบรูปแบบที่อาจมีหลายคอลัมน์ 1 หน้า ลำดับข้อความอาจคลาดเคลื่อน โปรดตรวจตัวอย่างก่อนส่ง')
  })
})
