/**
 * 照片相关API
 */
import http from './http'

/**
 * 扫描SD卡目录
 * @param {string} sdPath - SD卡路径
 */
export function scanDirectory(sdPath) {
  return http.post('/photos/scan', { sd_path: sdPath })
}

/**
 * 预览目录（不入库）
 * @param {string} sdPath - 目录路径
 */
export function previewDirectory(sdPath) {
  return http.post('/photos/scan/preview', { sd_path: sdPath })
}

/**
 * 整理到本地图库
 * @param {object} params - 整理参数
 */
export function importToLibrary(params) {
  return http.post('/photos/import', params)
}

/**
 * 查询照片列表
 * @param {object} params - 查询参数
 */
export function getPhotos(params = {}) {
  return http.get('/photos', { params })
}

/**
 * 获取单张照片详情
 * @param {number} photoId - 照片ID
 */
export function getPhotoDetail(photoId) {
  return http.get(`/photos/${photoId}`)
}

/**
 * 更新照片信息
 * @param {number} photoId - 照片ID
 * @param {object} updates - 更新内容
 */
export function updatePhoto(photoId, updates) {
  return http.patch(`/photos/${photoId}`, updates)
}

/**
 * 获取所有类别列表
 */
export function getCategories() {
  return http.get('/ai/categories')
}
