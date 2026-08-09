import pdfWorkerUrl from 'pdfjs-dist/build/pdf.worker.min.mjs?url'

import { MAX_PDF_PAGES, MAX_RAW_CHARS, pdfPageLimitMessage } from './document'

export type PdfExtraction = {
  pageCount: number
  text: string
  warnings: string[]
}

export type PdfExtractionOptions = {
  signal?: AbortSignal
  onProgress?: (completedPages: number, totalPages: number) => void
}

type PositionedText = {
  text: string
  x: number
  y: number
}

type PositionedLine = {
  y: number
  items: PositionedText[]
}

const LINE_Y_TOLERANCE = 3

// Every useful text item contributes at least one visible character. Reusing
// the raw-text ceiling also bounds hostile PDFs made from hundreds of thousands
// of blank or positioning-only items without rejecting an otherwise supported
// amount of extracted text.
const MAX_PDF_TEXT_ITEMS = MAX_RAW_CHARS

function pdfCharacterLimitMessage() {
  return `ข้อความที่ดึงจาก PDF ยาวเกินขีดจำกัด ${MAX_RAW_CHARS.toLocaleString()} ตัวอักษร ระบบจึงหยุดอ่านโดยไม่ตัดข้อความ และยังไม่ได้ส่งข้อมูลส่วนใดออกจากเครื่องคุณ โปรดแบ่งไฟล์หรือวางเฉพาะเนื้อหาที่ต้องการตรวจ`
}

function pdfTextItemLimitMessage() {
  return `PDF นี้มีชิ้นส่วนข้อความเกินขีดจำกัด ${MAX_PDF_TEXT_ITEMS.toLocaleString()} รายการ ระบบจึงหยุดอ่าน และยังไม่ได้ส่งข้อมูลส่วนใดออกจากเครื่องคุณ โปรดแบ่งไฟล์หรือวางเฉพาะเนื้อหาที่ต้องการตรวจ`
}

function throwIfAborted(signal?: AbortSignal) {
  if (signal?.aborted) throw new DOMException('ยกเลิกการอ่าน PDF', 'AbortError')
}

function removeHiddenControlCharacters(value: string) {
  let removed = 0
  const text = [...value].filter((character) => {
    const code = character.codePointAt(0) ?? 0
    const hiddenControl = code < 32 && code !== 9 && code !== 10 && code !== 13
    if (hiddenControl) removed += 1
    return !hiddenControl
  }).join('')
  return { text, removed }
}

function rebuildPageText(items: PositionedText[]) {
  const lines: PositionedLine[] = []
  const lineIndexesByYBucket = new Map<number, number[]>()

  for (const item of items) {
    let matchingLineIndex = -1

    if (Number.isFinite(item.y)) {
      const itemBucket = Math.floor(item.y / LINE_Y_TOLERANCE)
      for (const bucket of [itemBucket - 1, itemBucket, itemBucket + 1]) {
        for (const candidateIndex of lineIndexesByYBucket.get(bucket) ?? []) {
          const candidate = lines[candidateIndex]
          if (
            Math.abs(candidate.y - item.y) <= LINE_Y_TOLERANCE &&
            (matchingLineIndex === -1 || candidateIndex < matchingLineIndex)
          ) {
            // The previous implementation selected the first-created matching
            // line. Keep that tie-breaker when an item is within 3pt of two lines.
            matchingLineIndex = candidateIndex
          }
        }
      }
    }

    if (matchingLineIndex >= 0) {
      lines[matchingLineIndex].items.push(item)
      continue
    }

    const newLineIndex = lines.push({ y: item.y, items: [item] }) - 1
    if (Number.isFinite(item.y)) {
      const itemBucket = Math.floor(item.y / LINE_Y_TOLERANCE)
      const bucketLineIndexes = lineIndexesByYBucket.get(itemBucket)
      if (bucketLineIndexes) bucketLineIndexes.push(newLineIndex)
      else lineIndexesByYBucket.set(itemBucket, [newLineIndex])
    }
  }

  return lines
    .sort((left, right) => right.y - left.y)
    .map((line) => line.items.sort((left, right) => left.x - right.x).map((item) => item.text).join(' '))
    .join('\n')
    .replace(/[ \t]+/g, ' ')
    .replace(/\s+\n/g, '\n')
    .trim()
}

function looksMultiColumn(items: PositionedText[], pageWidth: number) {
  const lines = new Map<number, number[]>()
  for (const item of items) {
    const key = Math.round(item.y / 3) * 3
    const positions = lines.get(key)
    if (positions) positions.push(item.x)
    else lines.set(key, [item.x])
  }

  let linesWithWideGap = 0
  for (const positions of lines.values()) {
    positions.sort((left, right) => left - right)
    if (positions.some((position, index) => index > 0 && position - positions[index - 1] > pageWidth * 0.22)) linesWithWideGap += 1
  }
  return linesWithWideGap >= 3
}

export async function extractPdfText(file: File, options: PdfExtractionOptions = {}): Promise<PdfExtraction> {
  throwIfAborted(options.signal)
  const bytes = new Uint8Array(await file.arrayBuffer())
  const signature = new TextDecoder('ascii').decode(bytes.slice(0, 5))
  if (signature !== '%PDF-') throw new Error('ไฟล์ไม่มีโครงสร้าง PDF ที่ถูกต้อง')

  const { getDocument, GlobalWorkerOptions } = await import('pdfjs-dist')
  GlobalWorkerOptions.workerSrc = pdfWorkerUrl
  const loadingTask = getDocument({ data: bytes })

  try {
    const pdf = await loadingTask.promise
    // Checked before the extraction loop starts, so an oversized document costs
    // one document open rather than thousands of page renders. The `finally`
    // block below still destroys the loading task.
    if (pdf.numPages > MAX_PDF_PAGES) throw new Error(pdfPageLimitMessage(pdf.numPages))
    const pages: string[] = []
    let multiColumnPages = 0
    let processedTextItems = 0
    let processedTextCharacters = 0
    let extractedCharacterCount = 0
    let controlCharacterCount = 0

    for (let pageNumber = 1; pageNumber <= pdf.numPages; pageNumber += 1) {
      throwIfAborted(options.signal)
      const page = await pdf.getPage(pageNumber)
      const [content, viewport] = await Promise.all([page.getTextContent(), Promise.resolve(page.getViewport({ scale: 1 }))])

      processedTextItems += content.items.length
      if (processedTextItems > MAX_PDF_TEXT_ITEMS) {
        throw new Error(pdfTextItemLimitMessage())
      }

      const positionedItems: PositionedText[] = []
      for (const item of content.items) {
        if (!('str' in item)) continue
        processedTextCharacters += item.str.length
        if (processedTextCharacters > MAX_RAW_CHARS) throw new Error(pdfCharacterLimitMessage())
        if (!item.str.trim()) continue
        positionedItems.push({ text: item.str, x: item.transform[4], y: item.transform[5] })
      }
      if (looksMultiColumn(positionedItems, viewport.width)) multiColumnPages += 1
      const cleanedPage = removeHiddenControlCharacters(rebuildPageText(positionedItems))
      const pageSeparatorLength = pages.length === 0 ? 0 : 2
      extractedCharacterCount += pageSeparatorLength + cleanedPage.text.length
      if (extractedCharacterCount > MAX_RAW_CHARS) {
        throw new Error(pdfCharacterLimitMessage())
      }

      controlCharacterCount += cleanedPage.removed
      pages.push(cleanedPage.text)
      options.onProgress?.(pageNumber, pdf.numPages)
    }

    const text = pages.join('\n\n')
    const nonWhitespaceLength = text.replace(/\s/g, '').length
    const replacementCharacters = (text.match(/[\uFFFD]/g) ?? []).length
    const warnings: string[] = []

    if (nonWhitespaceLength === 0) {
      warnings.push('ไม่พบ text layer ใน PDF นี้ ซึ่งอาจเป็น PDF สแกน ระบบ MVP จะไม่ทำ OCR โปรดวางข้อความแทน')
    } else if (nonWhitespaceLength < Math.max(80, pdf.numPages * 20)) {
      warnings.push('ข้อความที่ดึงได้มีน้อยเมื่อเทียบกับจำนวนหน้า โปรดตรวจตัวอย่าง เพราะ PDF อาจเป็นภาพสแกนหรือดึงข้อความได้ไม่ครบ')
    }

    if (replacementCharacters > 0) {
      warnings.push('พบอักขระที่อ่านไม่ได้ในข้อความที่ดึงมา โปรดตรวจและแก้ไขก่อนยืนยัน')
    }
    if (controlCharacterCount > 0) {
      warnings.push('พบและนำอักขระควบคุมที่มองไม่เห็นออกจากข้อความ โปรดตรวจคำภาษาไทยและสระวรรณยุกต์ก่อนยืนยัน')
    }
    if (multiColumnPages > 0) {
      warnings.push(`ตรวจพบรูปแบบที่อาจมีหลายคอลัมน์ ${multiColumnPages} หน้า ลำดับข้อความอาจคลาดเคลื่อน โปรดตรวจตัวอย่างก่อนส่ง`)
    }

    return { pageCount: pdf.numPages, text, warnings }
  } finally {
    await loadingTask.destroy()
  }
}
