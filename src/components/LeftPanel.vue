<template>
  <div class="left-panel">
    <ChartBox title="机房分布" sub="location1" class="box">
      <BaseChart :option="roomOption" />
    </ChartBox>
    <ChartBox title="服务器型号分布" sub="model" class="box">
      <BaseChart :option="modelOption" />
    </ChartBox>
    <ChartBox title="负责人分布" sub="owner" class="box">
      <BaseChart :option="ownerOption" />
    </ChartBox>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import ChartBox from './ChartBox.vue'
import BaseChart from './BaseChart.vue'
import { data } from '../utils/data.js'

const PALETTE = ['#00e5ff', '#2f80ff', '#ffd166', '#21d07a', '#ff7eb6', '#9b8cff', '#ffb547']

const baseGrid = { left: 8, right: 16, top: 16, bottom: 8, containLabel: true }
const axisStyle = {
  axisLine: { lineStyle: { color: 'rgba(127,166,207,0.4)' } },
  axisLabel: { color: '#9fc3e8', fontSize: 12 },
  splitLine: { lineStyle: { color: 'rgba(127,166,207,0.12)' } }
}

const roomOption = computed(() => ({
  tooltip: { trigger: 'item', formatter: '{b}: {c} 台 ({d}%)' },
  legend: { show: false },
  series: [{
    type: 'pie',
    radius: ['38%', '68%'],
    center: ['50%', '52%'],
    roseType: 'radius',
    itemStyle: { borderColor: '#0a1733', borderWidth: 2, borderRadius: 4 },
    label: { color: '#cfe6ff', fontSize: 12, formatter: '{b}\n{c}' },
    labelLine: { length: 8, length2: 8 },
    data: data.roomDist.map((d, i) => ({ name: d.name, value: d.value, itemStyle: { color: PALETTE[i % PALETTE.length] } }))
  }]
}))

const modelOption = computed(() => ({
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  grid: { ...baseGrid, left: 8 },
  xAxis: { type: 'value', ...axisStyle },
  yAxis: { type: 'category', data: data.modelDist.map(d => d.name), ...axisStyle, inverse: true },
  series: [{
    type: 'bar',
    data: data.modelDist.map(d => d.value),
    barWidth: 12,
    itemStyle: {
      borderRadius: [0, 6, 6, 0],
      color: { type: 'linear', x: 0, y: 0, x2: 1, y2: 0, colorStops: [{ offset: 0, color: '#2f80ff' }, { offset: 1, color: '#00e5ff' }] }
    },
    label: { show: true, position: 'right', color: '#cfe6ff', fontSize: 12 }
  }]
}))

const ownerOption = computed(() => ({
  tooltip: { trigger: 'item', formatter: '{b}: {c} 台 ({d}%)' },
  legend: { bottom: 0, textStyle: { color: '#9fc3e8', fontSize: 11 }, itemWidth: 10, itemHeight: 10 },
  series: [{
    type: 'pie',
    radius: ['45%', '70%'],
    center: ['50%', '44%'],
    itemStyle: { borderColor: '#0a1733', borderWidth: 2 },
    label: { show: false },
    data: data.ownerDist.map((d, i) => ({ name: d.name, value: d.value, itemStyle: { color: PALETTE[i % PALETTE.length] } }))
  }]
}))
</script>

<style scoped>
.left-panel {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.box { flex: 1; min-height: 0; }
</style>
