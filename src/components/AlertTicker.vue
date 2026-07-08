<template>
  <div class="alert-ticker">
    <div class="at-head">
      <span class="at-title">实时告警</span>
      <span class="at-blink"></span>
      <span class="at-count">共 {{ alerts.length }} 条</span>
    </div>
    <div class="at-viewport">
      <div class="at-track" :style="{ animationDuration: duration + 's' }">
        <div v-for="(a, i) in loopList" :key="i" class="alert-row">
          <span class="alert-dot" :style="{ background: dotColor(a.level) }"></span>
          <span class="alert-host">{{ a.host }}</span>
          <span class="alert-metric">{{ a.metric }}</span>
          <span :style="{ color: dotColor(a.level), fontWeight: 700 }">{{ a.value }}{{ a.level === 'critical' ? '!' : '' }}</span>
          <span class="alert-time">{{ a.time }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { data } from '../utils/data.js'

const alerts = data.alerts
const loopList = computed(() => alerts.concat(alerts))
const duration = Math.max(20, alerts.length * 1.6)

function dotColor(level) {
  return level === 'critical' ? '#ff4d6d' : level === 'warn' ? '#ffb547' : '#21d07a'
}
</script>

<style scoped>
.alert-ticker {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  gap: 18px;
  padding: 0 18px;
  background: linear-gradient(90deg, rgba(0,229,255,0.06), rgba(47,128,255,0.02));
  border: 1px solid var(--panel-border);
  border-radius: 6px;
}
.at-head { display: flex; align-items: center; gap: 8px; flex: none; }
.at-title { font-size: 16px; font-weight: 700; color: #eaf6ff; letter-spacing: 2px; }
.at-blink { width: 9px; height: 9px; border-radius: 50%; background: #ff4d6d; box-shadow: 0 0 8px #ff4d6d; animation: blink 1s infinite; }
.at-count { font-size: 12px; color: var(--text-dim); }
.at-viewport { flex: 1; overflow: hidden; height: 26px; position: relative; }
.at-track { display: flex; flex-direction: column; gap: 4px; animation: scrollUp linear infinite; }
.at-viewport:hover .at-track { animation-play-state: paused; }
@keyframes scrollUp { from { transform: translateY(0); } to { transform: translateY(-50%); } }
@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.25; } }
</style>
