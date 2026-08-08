import { describe, expect, it } from 'vitest'

import {
  AnalysisRequestError,
  NETWORK_FAILURE_MESSAGE,
  UNEXPECTED_FAILURE_MESSAGE,
  WORKER_RESPONSE_FAILURE_MESSAGE,
  analysisErrorFromNetworkFailure,
  analysisErrorFromParseFailure,
  analysisErrorFromWorkerResponse,
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
    const unknownClientError = analysisErrorFromWorkerResponse({ error: 'คำขอไม่ถูกต้อง', code: 'NEW_CLIENT_ERROR' }, 418)
    const unknownServerError = analysisErrorFromWorkerResponse({ error: 'ระบบไม่พร้อม', code: 'NEW_SERVER_ERROR' }, 503)
    const errorShapedSuccess = analysisErrorFromWorkerResponse({ error: 'ไม่ควรเป็น payload สำเร็จ', code: 'NEW_SUCCESS_ERROR' }, 200)

    expect(unknownClientError).toMatchObject({ category: 'validation', retryable: false })
    expect(unknownServerError).toMatchObject({ category: 'service', retryable: true })
    expect(errorShapedSuccess).toMatchObject({ category: 'service', retryable: false })
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
