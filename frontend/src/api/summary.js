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
