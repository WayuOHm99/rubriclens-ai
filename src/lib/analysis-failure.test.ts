import { describe, expect, it } from 'vitest'

import {
  AnalysisRequestError,
  ANALYSIS_RETRY_COOLDOWN_MS,
  GEMINI_RATE_LIMIT_RETRY_COOLDOWN_MS,
  NETWORK_FAILURE_MESSAGE,
  UNEXPECTED_FAILURE_MESSAGE,
  WORKER_RESPONSE_FAILURE_MESSAGE,
  analysisErrorFromNetworkFailure,
  analysisErrorFromParseFailure,
  analysisErrorFromWorkerResponse,
  getAnalysisRetryPolicy,
  normalizeUnexpectedAnalysisError,
  shouldShowOfflineMascot,
  type AnalysisFailureCategory,
} from './analysis-failure'

describe('analysis failure classification', () => {
  it('keeps retryability separate from quota semantics', () => {
    const error = analysisErrorFromWorkerResponse({
      error: 'ส่งคำขอครบขีดจำกัดชั่วคราวแล้ว',
      code: 'RATE_LIMITED',
      retryable: true,
    }, 429)

    expect(error).toMatchObject({ category: 'quota', retryable: true, code: 'RATE_LIMITED' })
    expect(shouldShowOfflineMascot(error.category)).toBe(false)
  })

  it('recognizes a non-retryable configuration error as a service failure', () => {
    const error = analysisErrorFromWorkerResponse({
      error: 'ระบบ AI ยังตั้งค่าไม่สมบูรณ์',
      code: 'AI_CONFIGURATION',
      retryable: false,
    }, 503)

    expect(error).toMatchObject({ category: 'service', retryable: false, code: 'AI_CONFIGURATION' })
    expect(shouldShowOfflineMascot(error.category)).toBe(true)
  })

  it.each([
    ['DAILY_TOKEN_BUDGET', false],
    ['DAILY_REQUEST_BUDGET', false],
    ['GEMINI_DAILY_QUOTA', false],
    ['GEMINI_RATE_LIMIT', true],
    ['DAILY_FUTURE_GUARD', true],
  ])('classifies %s as quota regardless of retryability', (code, retryable) => {
    const error = analysisErrorFromWorkerResponse({ error: 'ถึงขีดจำกัดแล้ว', code, retryable }, 429)

    expect(error.category).toBe('quota')
    expect(error.retryable).toBe(retryable)
  })

  it.each([
    'AI_CONFIGURATION',
    'MODEL_UNAVAILABLE',
    'GEMINI_UNAVAILABLE',
    'GEMINI_TIMEOUT',
    'INVALID_AI_RESPONSE',
    'CONSOLIDATION_FAILED',
    'RATE_LIMIT_UNAVAILABLE',
    'INTERNAL_ERROR',
  ])('classifies %s as a service failure', (code) => {
    const error = analysisErrorFromWorkerResponse({ error: 'ระบบไม่พร้อม', code, retryable: false }, 503)

    expect(error.category).toBe('service')
    expect(shouldShowOfflineMascot(error.category)).toBe(true)
  })

  it('classifies idempotency conflicts separately from service failures', () => {
    const error = analysisErrorFromWorkerResponse({
      error: 'คีย์คำขอนี้ถูกใช้กับข้อมูลชุดอื่นไปแล้ว',
      code: 'IDEMPOTENCY_CONFLICT',
      retryable: false,
    }, 409)

    expect(error.category).toBe('conflict')
    expect(shouldShowOfflineMascot(error.category)).toBe(false)
  })

  it('classifies Worker API version errors as compatibility failures', () => {
    const error = analysisErrorFromWorkerResponse({
      error: 'หน้าเว็บและระบบตรวจเป็นคนละรุ่น',
      code: 'UNSUPPORTED_API_VERSION',
      retryable: false,
    }, 426)

    expect(error.category).toBe('compatibility')
    expect(shouldShowOfflineMascot(error.category)).toBe(false)
  })

  it.each([
    ['REQUEST_TOO_LARGE', 413],
    ['INVALID_REQUEST', 400],
    ['DOCUMENT_TOKEN_LIMIT', 413],
    ['EMPTY_RUBRIC', 400],
  ])('classifies known request/document error %s as validation', (code, status) => {
    const error = analysisErrorFromWorkerResponse({ error: 'ข้อมูลไม่ถูกต้อง', code, retryable: false }, status)

    expect(error.category).toBe('validation')
  })

  it('uses HTTP status as a conservative fallback for unknown Worker codes', () => {
    const unknownClientError = analysisErrorFromWorkerResponse({ error: 'รายละเอียดภายในที่ไม่ควรแสดง', code: 'NEW_CLIENT_ERROR' }, 418)
    const unknownServerError = analysisErrorFromWorkerResponse({ error: 'ระบบไม่พร้อม', code: 'NEW_SERVER_ERROR' }, 503)
    const errorShapedSuccess = analysisErrorFromWorkerResponse({ error: 'ไม่ควรเป็น payload สำเร็จ', code: 'NEW_SUCCESS_ERROR' }, 200)

    expect(unknownClientError).toMatchObject({ category: 'unexpected', retryable: false })
    expect(unknownClientError.message).not.toContain('รายละเอียดภายใน')
    expect(unknownServerError).toMatchObject({ category: 'service', retryable: true })
    expect(errorShapedSuccess).toMatchObject({ category: 'service', retryable: false })
  })

  it.each([
    [408, 'network'],
    [429, 'quota'],
    [409, 'conflict'],
    [426, 'compatibility'],
    [400, 'validation'],
    [413, 'validation'],
    [415, 'validation'],
    [422, 'validation'],
    [401, 'service'],
    [403, 'service'],
    [404, 'service'],
    [405, 'service'],
  ] satisfies Array<[number, AnalysisFailureCategory]>)('classifies status-only HTTP %s as %s without exposing its raw message', (status, category) => {
    const error = analysisErrorFromWorkerResponse({ error: `raw-internal-detail-${status}` }, status)

    expect(error.category).toBe(category)
    expect(error.message).not.toContain(`raw-internal-detail-${status}`)
  })

  it('keeps a known application code authoritative when its HTTP status is misleading', () => {
    const error = analysisErrorFromWorkerResponse({
      error: 'ระบบ AI ยังตั้งค่าไม่สมบูรณ์',
      code: 'AI_CONFIGURATION',
      retryable: false,
    }, 400)

    expect(error).toMatchObject({ category: 'service', code: 'AI_CONFIGURATION', retryable: false })
    expect(error.message).toBe('ระบบ AI ยังตั้งค่าไม่สมบูรณ์')
  })

  it.each(['NOT_FOUND', 'METHOD_NOT_ALLOWED'])('keeps endpoint code %s authoritative when its HTTP status is misleading', (code) => {
    const error = analysisErrorFromWorkerResponse({
      error: 'ไม่พบ endpoint ที่เรียกใช้',
      code,
      retryable: false,
    }, 400)

    expect(error).toMatchObject({ category: 'service', code, retryable: false })
  })

  it('uses a safe generic message when the Worker response cannot be read', () => {
    const error = analysisErrorFromWorkerResponse(undefined, 502)

    expect(error).toMatchObject({
      category: 'service',
      retryable: true,
      message: WORKER_RESPONSE_FAILURE_MESSAGE,
    })
  })
})

describe('explicit retry policy', () => {
  it.each([
    [{ category: 'network', code: 'NETWORK_FAILURE', retryable: true }, { mode: 'delayed', delayMs: ANALYSIS_RETRY_COOLDOWN_MS }],
    [{ category: 'service', code: 'GEMINI_TIMEOUT', retryable: true }, { mode: 'delayed', delayMs: ANALYSIS_RETRY_COOLDOWN_MS }],
    [{ category: 'service', code: 'GEMINI_UNAVAILABLE', retryable: true }, { mode: 'delayed', delayMs: ANALYSIS_RETRY_COOLDOWN_MS }],
    [{ category: 'quota', code: 'GEMINI_RATE_LIMIT', retryable: true }, { mode: 'delayed', delayMs: GEMINI_RATE_LIMIT_RETRY_COOLDOWN_MS }],
    [{ category: 'conflict', code: 'IDEMPOTENCY_CONFLICT', retryable: false }, { mode: 'immediate' }],
    [{ category: 'quota', code: 'RATE_LIMITED', retryable: true }, { mode: 'none' }],
    [{ category: 'quota', code: 'GEMINI_DAILY_QUOTA', retryable: false }, { mode: 'none' }],
    [{ category: 'service', code: 'AI_CONFIGURATION', retryable: false }, { mode: 'none' }],
    [{ category: 'compatibility', code: 'INCOMPATIBLE_VERSION', retryable: false }, { mode: 'none' }],
    [{ category: 'validation', code: 'INVALID_REQUEST', retryable: false }, { mode: 'none' }],
  ] as const)('maps $0 to $1', (failure, expected) => {
    expect(getAnalysisRetryPolicy(failure)).toEqual(expected)
  })
})

describe('client response parsing failures', () => {
  it('keeps an incompatible response separate from service failures', () => {
    const error = analysisErrorFromParseFailure({
      code: 'INCOMPATIBLE_VERSION',
      message: 'โปรดรีเฟรชหน้าแล้วลองใหม่',
      retryable: false,
    })

    expect(error).toMatchObject({ category: 'compatibility', retryable: false })
    expect(shouldShowOfflineMascot(error.category)).toBe(false)
  })

  it('treats an invalid response as a retryable service failure', () => {
    const error = analysisErrorFromParseFailure({
      code: 'INVALID_RESPONSE',
      message: 'ผลตอบกลับจากระบบยังไม่ครบถ้วน',
      retryable: true,
    })

    expect(error).toMatchObject({ category: 'service', retryable: true })
    expect(shouldShowOfflineMascot(error.category)).toBe(true)
  })
})

describe('safe client-side failures', () => {
  it('does not expose a raw network exception message', () => {
    const cause = new TypeError('Failed to fetch https://secret.internal.example')
    const error = analysisErrorFromNetworkFailure(cause)

    expect(error).toBeInstanceOf(AnalysisRequestError)
    expect(error).toMatchObject({ category: 'network', retryable: true, message: NETWORK_FAILURE_MESSAGE })
    expect(error.message).not.toContain('secret.internal.example')
    expect(error.cause).toBe(cause)
  })

  it.each([
    new Error('API key sk-secret must never reach the screen'),
    'database connection details',
    null,
  ])('normalizes an unexpected thrown value without exposing it: %s', (cause) => {
    const error = normalizeUnexpectedAnalysisError(cause)

    expect(error).toMatchObject({ category: 'unexpected', retryable: false, message: UNEXPECTED_FAILURE_MESSAGE })
    expect(error.message).not.toContain('sk-secret')
    expect(error.message).not.toContain('database')
  })

  it('does not replace an already classified analysis error', () => {
    const classified = analysisErrorFromNetworkFailure(new TypeError('offline'))

    expect(normalizeUnexpectedAnalysisError(classified)).toBe(classified)
  })

  it.each([
    ['validation', false],
    ['quota', false],
    ['compatibility', false],
    ['conflict', false],
    ['network', true],
    ['service', true],
    ['unexpected', true],
  ] satisfies Array<[AnalysisFailureCategory, boolean]>)('offline mascot for %s is %s', (category, expected) => {
    expect(shouldShowOfflineMascot(category)).toBe(expected)
  })
})
