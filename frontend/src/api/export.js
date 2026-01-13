/**
 * 导出相关API
 */
import http from './http'

/**
 * 导出精选照片
 * @param {object} params - 导出参数
 */
export function exportSelected(params) {
  return http.post('/export/selected', params)
}
