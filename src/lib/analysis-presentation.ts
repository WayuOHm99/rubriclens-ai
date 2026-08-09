import type { AnalysisFailureCategory } from './analysis-failure'

export function shouldShowOfflineMascot(category: AnalysisFailureCategory) {
  return category === 'network' || category === 'service' || category === 'unexpected'
}
