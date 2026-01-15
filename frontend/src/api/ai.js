/**
 * AI相关API
 */
import http from './http'

/**
 * AI分类照片
 * @param {number[]} photoIds - 照片ID列表
 * @param {number} maxWorkers - 并发线程数
 * @param {boolean} skipClassified - 跳过已分类照片
 */
export function classifyPhotos(photoIds, maxWorkers = 4, skipClassified = false) {
  const payload = {
    photo_ids: photoIds,
    max_workers: maxWorkers,
    skip_classified: skipClassified
  }
  console.log('AI classify request payload:', JSON.stringify(payload))
  console.log('photo_ids type:', typeof photoIds, 'isArray:', Array.isArray(photoIds))
  if (photoIds.length > 0) {
    console.log('First photo_id type:', typeof photoIds[0], 'value:', photoIds[0])
  }
  return http.post('/ai/classify', payload)
}
