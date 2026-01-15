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
    // 注意：error 字段可能是字符串或数组，只有非空字符串才视为错误
    if (data.error && typeof data.error === 'string') {
      ElMessage.error(data.message || data.error)
      return Promise.reject(new Error(data.error))
    }
    
    return data
  },
  (error) => {
    // 网络错误
    if (!error.response) {
      ElMessage.error('无法连接到服务器，请检查后端是否启动')
      return Promise.reject(error)
    }
    
    // HTTP错误
    const status = error.response.status
    const data = error.response.data
    const message = data?.message || data?.detail || error.message
    
    switch (status) {
      case 400:
        ElMessage.error(message || '请求参数有误')
        break
      case 404:
        ElMessage.error('请求的资源不存在')
        break
      case 500:
        ElMessage.error(message || '服务器内部错误，请稍后重试')
        break
      case 502:
      case 503:
        ElMessage.error('服务器暂时不可用，请稍后重试')
        break
      default:
        ElMessage.error(message || '请求失败，请稍后重试')
    }
    
    return Promise.reject(error)
  }
)

export default http
