/**
 * 总结相关API
 */
import http from './http'

/**
 * 生成拍摄总结
 * @param {object} params - 日期范围参数
 */
export function generateSummary(params = {}) {
  return http.post('/summary/generate', params)
}

/**
 * 获取快速统计
 */
export function getQuickStats() {
  return http.get('/summary/quick-stats')
}

/**
 * 获取历史总结列表
 * @param {number} limit - 返回数量限制
 */
export function getSummaryHistory(limit = 20) {
  return http.get('/summary/history', { params: { limit } })
}

/**
 * 获取历史总结详情
 * @param {number} historyId - 历史记录ID
 */
export function getSummaryHistoryDetail(historyId) {
  return http.get(`/summary/history/${historyId}`)
}

/**
 * 删除历史总结
 * @param {number} historyId - 历史记录ID
 */
export function deleteSummaryHistory(historyId) {
  return http.delete(`/summary/history/${historyId}`)
}
