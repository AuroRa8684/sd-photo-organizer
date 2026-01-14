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

/**
 * 批量删除照片
 * @param {number[]} photoIds - 照片ID列表
 */
export function batchDeletePhotos(photoIds) {
  return http.delete('/photos/batch', { data: { photo_ids: photoIds } })
}

/**
 * 批量更新照片
 * @param {number[]} photoIds - 照片ID列表
 * @param {object} updates - 更新内容 {category?, is_selected?}
 */
export function batchUpdatePhotos(photoIds, updates) {
  return http.patch('/photos/batch', { photo_ids: photoIds, ...updates })
}

/**
 * 获取系统驱动器列表
 */
export function getSystemDrives() {
  return http.get('/photos/system/drives')
}

/**
 * 浏览目录
 * @param {string} path - 目录路径
 */
export function browseDirectory(path = '') {
  return http.get('/photos/system/browse', { params: { path } })
}
