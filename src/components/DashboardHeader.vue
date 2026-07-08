<template>
  <header class="dash-header">
    <dv-decoration-8 :color="['#00e5ff', '#2f80ff']" style="width: 320px; height: 50px;" />

    <div class="header-center">
      <dv-decoration-5 style="width: 100%; height: 30px;" :color="['#00e5ff', '#2f80ff']" />
      <h1 class="title">
        <span class="star">✦</span>
        星枢 · 服务器集群监控大屏
        <span class="star">✦</span>
      </h1>
      <div class="subtitle">StarHubClusterMonitor · HiSmartLab 集群态势感知中心</div>
    </div>

    <div class="header-right">
      <div class="meta">
        <span class="meta-item">节点 <b>{{ meta.hostCount }}</b></span>
        <span class="meta-item">指标 <b>{{ meta.modCount }}</b></span>
        <span class="meta-item">数据区间 <b>{{ meta.timeRange.start }} ~ {{ meta.timeRange.end }}</b></span>
      </div>
      <div class="clock">{{ clock }}</div>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { data } from '../utils/data.js'

const meta = data.meta
const clock = ref('')
let timer = null

function tick() {
  const d = new Date()
  const p = (n) => String(n).padStart(2, '0')
  clock.value = `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}`
}

onMounted(() => {
  tick()
  timer = setInterval(tick, 1000)
})
onBeforeUnmount(() => clearInterval(timer))
</script>

<style scoped>
.dash-header {
  height: 92px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
}
.header-center {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  text-align: center;
  width: 720px;
}
.title {
  font-size: 38px;
  font-weight: 800;
  letter-spacing: 6px;
  margin-top: 2px;
  background: linear-gradient(180deg, #ffffff 0%, var(--gold) 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 0 0 18px rgba(255, 209, 102, 0.25);
}
.title .star { color: var(--cyan); -webkit-text-fill-color: var(--cyan); font-size: 24px; margin: 0 10px; }
.subtitle { font-size: 13px; color: var(--text-dim); letter-spacing: 2px; margin-top: 2px; }
.header-right { text-align: right; }
.meta { font-size: 13px; color: var(--text-dim); display: flex; gap: 16px; justify-content: flex-end; }
.meta-item b { color: var(--cyan); font-weight: 700; }
.clock { font-size: 20px; color: var(--gold); font-weight: 700; margin-top: 6px; font-family: "Bahnschrift", sans-serif; letter-spacing: 1px; }
</style>
