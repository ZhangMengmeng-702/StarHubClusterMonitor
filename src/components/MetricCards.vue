<template>
  <div class="metric-row">
    <div class="metric-card" v-for="c in cards" :key="c.key">
      <div class="label">{{ c.label }}</div>
      <div class="value-line">
        <dv-digital-flop :config="c.flop" style="width: 130px; height: 38px;" />
        <span class="unit">{{ c.unit }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { data } from '../utils/data.js'

const o = data.overview

const cards = computed(() => [
  { key: 'total', label: '集群节点总数', unit: '台', flop: { number: [o.totalHosts], content: '{nt}', style: { fontSize: 30, fill: '#ffd166', fontWeight: 800 } } },
  { key: 'online', label: '在线节点', unit: '台', flop: { number: [o.onlineHosts], content: '{nt}', style: { fontSize: 30, fill: '#21d07a', fontWeight: 800 } } },
  { key: 'cpu', label: '平均CPU使用率', unit: '%', flop: { number: [o.avgCpu], content: '{nt}', style: { fontSize: 30, fill: '#00e5ff', fontWeight: 800 } } },
  { key: 'disk', label: '平均磁盘利用率', unit: '%', flop: { number: [o.avgDisk], content: '{nt}', style: { fontSize: 30, fill: '#2f80ff', fontWeight: 800 } } },
  { key: 'alert', label: '活跃告警', unit: '条', flop: { number: [o.alertCount], content: '{nt}', style: { fontSize: 30, fill: '#ff4d6d', fontWeight: 800 } } }
])
</script>

<style scoped>
.metric-row {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 14px;
  height: 100%;
}
.value-line { display: flex; align-items: baseline; }
</style>
