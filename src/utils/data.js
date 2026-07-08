// 大屏数据入口
// 策略：先用本地静态 JSON 兜底（首屏秒开），再调用后端 /api/dashboard，
// 每 30s 轮询一次，实现"实时"刷新。后端不可用时自动回退到静态数据。
import { reactive } from 'vue'
import fallback from '../data/dashboard_data.json'

export const data = reactive(JSON.parse(JSON.stringify(fallback)))
export const isLive = reactive({ value: false })

async function load() {
    try {
        const res = await fetch('/api/dashboard')
        if (!res.ok) throw new Error('HTTP ' + res.status)
        Object.assign(data, await res.json())
        isLive.value = true
    } catch (e) {
        // 后端不可用：保留静态兜底数据，仅首屏可见
        console.warn('[data] 后端 API 不可用，使用本地静态数据兜底：', e.message)
    }
}

load()
setInterval(load, 30000)

export default data
