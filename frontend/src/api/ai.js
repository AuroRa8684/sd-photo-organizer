/**
 * AI相关API
 */
import http from './http'

/**
 * AI分类照片
 * @param {number[]} photoIds - 照片ID列表
 * @param {number} maxWorkers - 并发线程数
 */
export function classifyPhotos(photoIds, maxWorkers = 4) {
  return http.post('/ai/classify', {
    photo_ids: photoIds,
    max_workers: maxWorkers
  })
}
