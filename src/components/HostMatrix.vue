<template>
  <div class="host-matrix">
    <div
      v-for="h in hosts"
      :key="h.hostid"
      class="host-node"
      :style="nodeStyle(h)"
      :title="`${h.hostid} | ${h.model} | ${h.location1}机房\nCPU ${h.cpu}% · 内存 ${h.mem}% · 磁盘 ${h.disk}% · 负载 ${h.load}`"
    >
      <span class="hid">{{ h.hostid.replace('host', 'H') }}</span>
      <span class="hval">CPU {{ h.cpu }}%</span>
      <span class="hval">磁盘 {{ h.disk }}%</span>
    </div>
  </div>
</template>

<script setup>
import { data } from '../utils/data.js'
const hosts = data.hostStatus

function colorFor(status) {
  if (status === 'critical') return { bg: 'rgba(255,77,109,0.30)', border: '#ff4d6d', glow: 'rgba(255,77,109,0.6)' }
  if (status === 'warn') return { bg: 'rgba(255,181,71,0.26)', border: '#ffb547', glow: 'rgba(255,181,71,0.5)' }
  return { bg: 'rgba(33,208,122,0.22)', border: '#21d07a', glow: 'rgba(33,208,122,0.45)' }
}

function nodeStyle(h) {
  const c = colorFor(h.status)
  return {
    background: c.bg,
    borderColor: c.border,
    boxShadow: `0 0 10px ${c.glow}`
  }
}
</script>

<style scoped>
.host-matrix {
  width: 100%;
  height: 100%;
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  grid-template-rows: repeat(4, 1fr);
  gap: 10px;
  padding: 4px;
}
.host-node { gap: 2px; }
</style>
