/**
 * Axios HTTP 客户端封装
 * 统一处理请求/响应拦截、错误处理
 */
import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建axios实例
const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000',
  timeout: 120000, // 120秒超时（AI调用可能较慢）
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
http.interceptors.request.use(
  (config) => {
    // 可以在这里添加token等认证信息
    return config
  },
  (error) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
http.interceptors.response.use(
  (response) => {
    const data = response.data
    
    // 处理统一响应格式
    if (data.error) {
      ElMessage.error(data.error)
      return Promise.reject(new Error(data.error))
    }
    
    return data
  },
  (error) => {
    // 网络错误
    if (!error.response) {
      ElMessage.error('网络错误，请检查后端服务是否启动')
      return Promise.reject(error)
    }
    
    // HTTP错误
    const status = error.response.status
    const message = error.response.data?.detail || error.message
    
    switch (status) {
      case 404:
        ElMessage.error('请求的资源不存在')
        break
      case 500:
        ElMessage.error(`服务器错误: ${message}`)
        break
      default:
        ElMessage.error(message || '请求失败')
    }
    
    return Promise.reject(error)
  }
)

export default http
