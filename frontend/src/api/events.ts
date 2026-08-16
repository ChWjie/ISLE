/**
 * Events API Service
 */
import apiClient from './client'
import { apiUrl } from './config'

export interface Event {
    id: number
    event_id: string
    name: string
    description?: string
    dispute_type?: string
    our_side: string[]
    opponent_side: string[]
    legal_systems: string[]
    fact_summary?: string
    created_at: string
    updated_at: string
}

const eventsApi = {
    // Load event list
    async listEvents(): Promise<Event[]> {
        try {
            return await apiClient.get('/api/v1/events')
        } catch (error) {
            console.warn('[events] apiClient failed, fallback fetch list:', error)
            const response = await fetch(apiUrl('/api/v1/events'))
            if (!response.ok) throw new Error(`Failed to load events: ${response.status}`)
            const data = await response.json()
            return data?.code === 200 ? data.data : data
        }
    },

    // Load event detail; fallback to list matching by event_id/id
    async getEvent(eventId: string): Promise<Event> {
        try {
            return await apiClient.get(`/api/v1/events/${eventId}`)
        } catch (error) {
            console.warn('[events] getEvent failed, fallback list match:', eventId, error)
            const events = await this.listEvents()
            const matched = events.find(item =>
                String(item.event_id) === String(eventId) ||
                String(item.id) === String(eventId)
            )
            if (!matched) {
                console.warn('[events] event not found, fallback first event:', eventId)
                const firstEvent = events[0]
                if (firstEvent) return firstEvent
                throw error
            }
            return matched
        }
    },

    // Create event
    async createEvent(data: Partial<Event>): Promise<Event> {
        return apiClient.post('/api/v1/events', data)
    }
}

export default eventsApi
