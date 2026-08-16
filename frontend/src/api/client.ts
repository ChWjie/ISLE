/**
 * API Base Configuration
 */
import axios from 'axios'
import { repairMojibakeDeep } from './text'
import { API_BASE_URL } from './config'

console.info('[API_BASE_URL]', API_BASE_URL || '(same origin)')
if (location.protocol === 'https:' && API_BASE_URL.startsWith('http://')) {
    console.warn('[API_BASE_URL] 当前前端是 HTTPS，但后端是 HTTP，浏览器可能会拦截请求。')
}

const apiClient = axios.create({
    baseURL: API_BASE_URL,
    timeout: 60000,
    headers: {
        'Content-Type': 'application/json'
    }
})

// Response interceptor
apiClient.interceptors.response.use(
    (response) => {
        // 统一处理 BaseResponse 格式
        if (response.data && response.data.code === 200) {
            return repairMojibakeDeep(response.data.data)
        }
        return repairMojibakeDeep(response.data)
    },
    (error) => {
        console.error('API Error:', error)
        throw error
    }
)

export default apiClient
