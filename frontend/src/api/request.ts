import axios from 'axios'
import type { AxiosInstance, AxiosResponse } from 'axios'
import { API_BASE_URL } from './config'

// 创建axios实例
const service: AxiosInstance = axios.create({
    baseURL: API_BASE_URL,
    timeout: 120000,
})

// 请求拦截器
service.interceptors.request.use(
    (config) => {
        // 添加token
        const token = localStorage.getItem('token')
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    (error) => {
        console.error('请求错误:', error)
        return Promise.reject(error)
    }
)

// 响应拦截器
service.interceptors.response.use(
    (response: AxiosResponse) => {
        return response.data
    },
    (error) => {
        console.error('响应错误:', error)

        if (error.response) {
            switch (error.response.status) {
                case 401:
                    // 未授权，跳转登录
                    localStorage.removeItem('token')
                    window.location.href = '/login'
                    break
                case 403:
                    console.error('没有权限')
                    break
                case 404:
                    console.error('请求的资源不存在')
                    break
                case 500:
                    console.error('服务器错误')
                    break
            }
        }

        return Promise.reject(error)
    }
)

export default service
