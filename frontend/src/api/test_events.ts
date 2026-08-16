/**
 * 快速测试脚本 - 检查Events API返回格式
 */
import eventsApi from './events'

async function testEventsAPI() {
    try {
        console.log('Testing Events API...')
        const events = await eventsApi.listEvents()
        console.log('Total events:', events.length)
        console.log('First event:', JSON.stringify(events[0], null, 2))

        // Check required fields
        const requiredFields = ['id', 'event_id', 'name', 'created_at']
        const firstEvent = events[0] as Record<string, unknown> | undefined
        if (!firstEvent) {
            console.warn('No events returned')
            return
        }
        requiredFields.forEach(field => {
            if (!firstEvent[field]) {
                console.error(`Missing field: ${field}`)
            } else {
                console.log(`✓ ${field}: ${firstEvent[field]}`)
            }
        })
    } catch (error) {
        console.error('API Test Failed:', error)
    }
}

// Uncomment to run:
// testEventsAPI()

export default testEventsAPI
