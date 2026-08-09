export const ANALYSIS_FAILURE_CATEGORIES = [
  'validation',
  'quota',
  'compatibility',
  'conflict',
  'network',
  'service',
  'unexpected',
] as const

export type AnalysisFailureCategory = (typeof ANALYSIS_FAILURE_CATEGORIES)[number]

export type AnalysisRetryPolicy =
  | { mode: 'immediate' }
  | { mode: 'delayed'; delayMs: number }
  | { mode: 'none' }

export const ANALYSIS_RETRY_COOLDOWN_MS = 10_000
export const GEMINI_RATE_LIMIT_RETRY_COOLDOWN_MS = 60_000

export type WorkerErrorPayload = {
  error: string
  code?: string
  retryable?: boolean
}

export type AnalysisParseFailure = {
  code: 'INCOMPATIBLE_VERSION' | 'INVALID_RESPONSE'
  message: string
  retryable: boolean
}

type AnalysisRequestErrorOptions = {
  category: AnalysisFailureCategory
  code: string
  message: string
  retryable: boolean
  cause?: unknown
}

/**
 * A user-safe analysis failure. `category` describes what failed, while
 * `retryable` only answers whether repeating the same request can help.
 */
export class AnalysisRequestError extends Error {
  readonly category: AnalysisFailureCategory
  readonly code: string
  readonly retryable: boolean

  constructor(options: AnalysisRequestErrorOptions) {
    super(options.message, { cause: options.cause })
    this.name = 'AnalysisRequestError'
    this.category = options.category
    this.code = options.code
    this.retryable = options.retryable
  }
}

type AnalysisRetryContext = Pick<AnalysisRequestError, 'category' | 'code' | 'retryable'>

/** Keeps presentation retry rules explicit instead of treating every retryable error alike. */
export function getAnalysisRetryPolicy(failure: AnalysisRetryContext): AnalysisRetryPolicy {
  if (failure.category === 'conflict') return { mode: 'immediate' }
  if (failure.code === 'GEMINI_RATE_LIMIT') {
    return { mode: 'delayed', delayMs: GEMINI_RATE_LIMIT_RETRY_COOLDOWN_MS }
  }
  if (failure.category === 'network' || (failure.category === 'service' && failure.retryable)) {
    return { mode: 'delayed', delayMs: ANALYSIS_RETRY_COOLDOWN_MS }
  }
  return { mode: 'none' }
}

export const NETWORK_FAILURE_MESSAGE = 'ไม่สามารถเชื่อมต่อระบบตรวจเอกสารได้ จึงยืนยันไม่ได้ว่าคำขอถูกส่งถึงระบบหรือไม่ โปรดตรวจการเชื่อมต่ออินเทอร์เน็ตก่อนลองใหม่'
export const UNEXPECTED_FAILURE_MESSAGE = 'หน้าเว็บเกิดข้อผิดพลาดที่ไม่คาดคิด จึงยืนยันไม่ได้ว่าคำขอถูกส่งถึงระบบหรือไม่ โปรดเริ่มใหม่ภายหลัง'
export const WORKER_RESPONSE_FAILURE_MESSAGE = 'ระบบได้รับคำขอแล้ว แต่ตอบกลับในรูปแบบที่อ่านไม่ได้ โปรดลองใหม่ภายหลัง'

const STATUS_ONLY_MESSAGES: Partial<Record<number, string>> = {
  400: 'ระบบได้รับคำขอแล้ว แต่ข้อมูลที่ส่งไม่ถูกต้อง โปรดตรวจเอกสารและเกณฑ์ก่อนส่งใหม่',
  401: 'ระบบได้รับคำขอแล้ว แต่หน้าเว็บยังเข้าถึงระบบตรวจไม่ได้ กรุณาแจ้งผู้ดูแลระบบ',
  403: 'ระบบได้รับคำขอแล้ว แต่หน้าเว็บไม่ได้รับอนุญาตให้ใช้ระบบตรวจ กรุณาแจ้งผู้ดูแลระบบ',
  404: 'ระบบได้รับคำขอแล้ว แต่ไม่พบ endpoint สำหรับตรวจเอกสาร กรุณาแจ้งผู้ดูแลระบบ',
  405: 'ระบบได้รับคำขอแล้ว แต่ endpoint ไม่รองรับวิธีส่งคำขอนี้ กรุณาแจ้งผู้ดูแลระบบ',
  408: 'ระบบได้รับคำขอแล้ว แต่ตอบกลับไม่ทันเวลา โปรดรอ 10 วินาทีก่อนลองใหม่ด้วยคำขอเดิม',
  409: 'ระบบได้รับคำขอแล้ว แต่รหัสคำขอเดิมขัดแย้งกับข้อมูลที่ส่ง กดลองอีกครั้งเพื่อสร้างรหัสใหม่',
  413: 'ระบบได้รับคำขอแล้ว แต่เอกสารมีขนาดเกินที่รองรับ โปรดลดขนาดเอกสารก่อนส่งใหม่',
  415: 'ระบบได้รับคำขอแล้ว แต่รูปแบบข้อมูลไม่รองรับ โปรดกลับไปเตรียมเอกสารใหม่',
  422: 'ระบบได้รับคำขอแล้ว แต่ข้อมูลยังไม่ครบหรือไม่ถูกต้อง โปรดตรวจเอกสารและเกณฑ์ก่อนส่งใหม่',
  426: 'ระบบได้รับคำขอแล้ว แต่หน้าเว็บกับระบบตรวจเป็นคนละรุ่น โปรดรีเฟรชหน้าเว็บก่อนลองใหม่',
  429: 'ระบบได้รับคำขอแล้ว แต่ถึงขีดจำกัดการใช้งาน โปรดลองใหม่ในชั่วโมงถัดไป',
}

const UNKNOWN_WORKER_FAILURE_MESSAGE = 'ระบบได้รับคำขอแล้ว แต่ตอบกลับด้วยข้อผิดพลาดที่ไม่รู้จัก กรุณาลองใหม่ภายหลัง'

const QUOTA_CODES = new Set([
  'RATE_LIMITED',
  'GEMINI_DAILY_QUOTA',
  'GEMINI_RATE_LIMIT',
])

const COMPATIBILITY_CODES = new Set([
  'UNSUPPORTED_API_VERSION',
  'INCOMPATIBLE_VERSION',
])

const CONFLICT_CODES = new Set([
  'IDEMPOTENCY_CONFLICT',
])

const SERVICE_CODES = new Set([
  'AI_CONFIGURATION',
  'MODEL_UNAVAILABLE',
  'GEMINI_UNAVAILABLE',
  'GEMINI_TIMEOUT',
  'INVALID_AI_RESPONSE',
  'CONSOLIDATION_FAILED',
  'RATE_LIMIT_UNAVAILABLE',
  'INTERNAL_ERROR',
  'NOT_FOUND',
  'METHOD_NOT_ALLOWED',
])

const VALIDATION_CODES = new Set([
  'REQUEST_TOO_LARGE',
  'MISSING_BODY',
  'INVALID_JSON',
  'UNSUPPORTED_CONTENT_TYPE',
  'INVALID_IDEMPOTENCY_KEY',
  'INVALID_REQUEST',
  'APPENDIX_CONFIRMATION_REQUIRED',
  'EMPTY_MAIN_DOCUMENT',
  'DOCUMENT_CHAR_LIMIT',
  'DOCUMENT_TOKEN_LIMIT',
  'CONSOLIDATION_INPUT_TOO_LARGE',
  'EMPTY_RUBRIC',
  'REQUEST_CANCELLED',
])

function classifyKnownWorkerCode(code: string | undefined): AnalysisFailureCategory | undefined {
  if (code?.startsWith('DAILY_') || (code && QUOTA_CODES.has(code))) return 'quota'
  if (code && CONFLICT_CODES.has(code)) return 'conflict'
  if (code && COMPATIBILITY_CODES.has(code)) return 'compatibility'
  if (code && SERVICE_CODES.has(code)) return 'service'
  if (code && VALIDATION_CODES.has(code)) return 'validation'
  return undefined
}

function classifyWorkerError(code: string | undefined, status: number): AnalysisFailureCategory {
  // A successful HTTP response containing an error object is a broken service
  // contract, even if the embedded code resembles a client validation error.
  if (status >= 200 && status < 300) return 'service'

  const knownCodeCategory = classifyKnownWorkerCode(code)
  if (knownCodeCategory) return knownCodeCategory

  if (status === 408) return 'network'
  if (status === 429) return 'quota'
  if (status === 409) return 'conflict'
  if (status === 426) return 'compatibility'
  if ([400, 413, 415, 422].includes(status)) return 'validation'
  if ([401, 403, 404, 405].includes(status)) return 'service'
  if (status >= 500) return 'service'
  return 'unexpected'
}

function safeFallbackMessage(status: number, category: AnalysisFailureCategory) {
  const statusMessage = STATUS_ONLY_MESSAGES[status]
  if (statusMessage) return statusMessage
  if (category === 'service') return WORKER_RESPONSE_FAILURE_MESSAGE
  return UNKNOWN_WORKER_FAILURE_MESSAGE
}

/** Converts a parsed Worker error response without inferring semantics from retryability. */
export function analysisErrorFromWorkerResponse(payload: WorkerErrorPayload | undefined, status: number) {
  const workerCode = payload?.code?.trim()
  const code = workerCode || (payload ? `HTTP_${status}_ERROR` : 'UNREADABLE_WORKER_RESPONSE')
  const category = classifyWorkerError(workerCode, status)
  const retryable = payload?.retryable ?? (status === 408 || status >= 500)
  const hasAuthoritativeCode = !(status >= 200 && status < 300) && Boolean(classifyKnownWorkerCode(workerCode))
  const message = hasAuthoritativeCode
    ? payload?.error.trim() || safeFallbackMessage(status, category)
    : safeFallbackMessage(status, category)

  return new AnalysisRequestError({
    category,
    code,
    message,
    retryable,
  })
}

/** Converts failures returned by the browser-side response contract parser. */
export function analysisErrorFromParseFailure(failure: AnalysisParseFailure) {
  return new AnalysisRequestError({
    category: failure.code === 'INCOMPATIBLE_VERSION' ? 'compatibility' : 'service',
    code: failure.code,
    message: failure.message,
    retryable: failure.retryable,
  })
}

/** Wraps fetch/response-stream failures without exposing browser or URL details. */
export function analysisErrorFromNetworkFailure(cause?: unknown) {
  return new AnalysisRequestError({
    category: 'network',
    code: 'NETWORK_FAILURE',
    message: NETWORK_FAILURE_MESSAGE,
    retryable: true,
    cause,
  })
}

/** Keeps classified failures intact and hides details from all other thrown values. */
export function normalizeUnexpectedAnalysisError(cause: unknown) {
  if (cause instanceof AnalysisRequestError) return cause

  return new AnalysisRequestError({
    category: 'unexpected',
    code: 'UNEXPECTED_ERROR',
    message: UNEXPECTED_FAILURE_MESSAGE,
    retryable: false,
    cause,
  })
}
