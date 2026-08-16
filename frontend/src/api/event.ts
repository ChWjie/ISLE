import request from './request'
import type { DisputeEvent, EventStats } from '@/types'

export const eventApi = {
    // 获取事件列表
    getEvents: (params?: { type?: string; status?: string; skip?: number; limit?: number }) =>
        request.get<DisputeEvent[]>('/api/v1/events', { params }),

    // 获取事件详情
    getEventById: (id: string) =>
        request.get<DisputeEvent>(`/api/v1/events/${id}`),

    // 获取事件统计
    getEventStats: () =>
        request.get<EventStats>('/api/v1/events/stats'),

    // 创建事件
    createEvent: (data: Partial<DisputeEvent>) =>
        request.post<DisputeEvent>('/api/v1/events', data),

    // 更新事件
    updateEvent: (id: string, data: Partial<DisputeEvent>) =>
        request.put<DisputeEvent>(`/api/v1/events/${id}`, data),

    // 删除事件
    deleteEvent: (id: string) =>
        request.delete(`/api/v1/events/${id}`),
}
