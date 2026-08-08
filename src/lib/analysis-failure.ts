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

export const NETWORK_FAILURE_MESSAGE = 'ไม่สามารถเชื่อมต่อระบบตรวจเอกสารได้ โปรดตรวจการเชื่อมต่ออินเทอร์เน็ตแล้วลองใหม่อีกครั้ง'
export const UNEXPECTED_FAILURE_MESSAGE = 'เกิดข้อผิดพลาดที่ไม่คาดคิดในหน้าเว็บ โปรดลองใหม่ภายหลัง'
export const WORKER_RESPONSE_FAILURE_MESSAGE = 'ระบบตอบกลับในรูปแบบที่อ่านไม่ได้ โปรดลองใหม่ภายหลัง'

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

function classifyWorkerError(code: string | undefined, status: number): AnalysisFailureCategory {
  // A successful HTTP response containing an error object is a broken service
  // contract, even if the embedded code resembles a client validation error.
  if (status >= 200 && status < 300) return 'service'

  if (code?.startsWith('DAILY_') || (code && QUOTA_CODES.has(code))) return 'quota'
  if (code && CONFLICT_CODES.has(code)) return 'conflict'
  if (code && COMPATIBILITY_CODES.has(code)) return 'compatibility'
  if (code && SERVICE_CODES.has(code)) return 'service'
  if (code && VALIDATION_CODES.has(code)) return 'validation'

  if (status >= 500) return 'service'
  if (status >= 400 && status < 500) return 'validation'
  return 'unexpected'
}

/** Converts a parsed Worker error response without inferring semantics from retryability. */
export function analysisErrorFromWorkerResponse(payload: WorkerErrorPayload | undefined, status: number) {
  const code = payload?.code?.trim() || (payload ? `HTTP_${status}_ERROR` : 'UNREADABLE_WORKER_RESPONSE')
  const retryable = payload?.retryable ?? status >= 500
  const message = payload?.error.trim() || WORKER_RESPONSE_FAILURE_MESSAGE

  return new AnalysisRequestError({
    category: classifyWorkerError(code, status),
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

export function shouldShowOfflineMascot(category: AnalysisFailureCategory) {
  return category === 'network' || category === 'service' || category === 'unexpected'
}
