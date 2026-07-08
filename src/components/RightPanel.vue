<template>
  <div class="right-panel">
    <ChartBox title="磁盘 I/O TOP" sub="主机平均磁盘利用率 %" class="box">
      <BaseChart :option="diskOption" />
    </ChartBox>
    <ChartBox title="网络流量" sub="入站 / 出站 MB/s" class="box">
      <BaseChart :option="netOption" />
    </ChartBox>
    <ChartBox title="系统负载 & 进程" sub="load1 / 运行进程数" class="box">
      <BaseChart :option="loadOption" />
    </ChartBox>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import ChartBox from './ChartBox.vue'
import BaseChart from './BaseChart.vue'
import { data } from '../utils/data.js'

const t = data.perfTrend
const axisStyle = {
  axisLine: { lineStyle: { color: 'rgba(127,166,207,0.4)' } },
  axisLabel: { color: '#9fc3e8', fontSize: 11 },
  splitLine: { lineStyle: { color: 'rgba(127,166,207,0.12)' } }
}

const diskOption = computed(() => {
  const sorted = [...data.diskTop].sort((a, b) => a.value - b.value)
  return {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: 8, right: 24, top: 10, bottom: 6, containLabel: true },
    xAxis: { type: 'value', ...axisStyle },
    yAxis: { type: 'category', data: sorted.map(d => d.name), ...axisStyle },
    series: [{
      type: 'bar', data: sorted.map(d => d.value), barWidth: 11,
      itemStyle: {
        borderRadius: [0, 6, 6, 0],
        color: { type: 'linear', x: 0, y: 0, x2: 1, y2: 0, colorStops: [{ offset: 0, color: '#2f80ff' }, { offset: 1, color: '#00e5ff' }] }
      },
      label: { show: true, position: 'right', color: '#cfe6ff', fontSize: 11, formatter: '{c}%' }
    }]
  }
})

const netOption = computed(() => ({
  tooltip: { trigger: 'axis', backgroundColor: 'rgba(10,23,51,0.9)', borderColor: '#00e5ff', textStyle: { color: '#cfe6ff' } },
  legend: { top: 2, textStyle: { color: '#9fc3e8', fontSize: 11 }, itemWidth: 12, itemHeight: 8 },
  grid: { left: 8, right: 12, top: 34, bottom: 20, containLabel: true },
  xAxis: { type: 'category', data: t.times, boundaryGap: false, axisLine: { lineStyle: { color: 'rgba(127,166,207,0.4)' } }, axisLabel: { color: '#9fc3e8', fontSize: 10, interval: Math.floor(t.times.length / 6) } },
  yAxis: { type: 'value', ...axisStyle },
  series: [
    areaLine('入站', t.netIn, '#00e5ff'),
    areaLine('出站', t.netOut, '#ffd166')
  ]
}))

const loadOption = computed(() => ({
  tooltip: { trigger: 'axis', backgroundColor: 'rgba(10,23,51,0.9)', borderColor: '#00e5ff', textStyle: { color: '#cfe6ff' } },
  legend: { top: 2, textStyle: { color: '#9fc3e8', fontSize: 11 }, itemWidth: 12, itemHeight: 8 },
  grid: { left: 8, right: 12, top: 34, bottom: 20, containLabel: true },
  xAxis: { type: 'category', data: t.times, boundaryGap: false, axisLine: { lineStyle: { color: 'rgba(127,166,207,0.4)' } }, axisLabel: { color: '#9fc3e8', fontSize: 10, interval: Math.floor(t.times.length / 6) } },
  yAxis: [
    { type: 'value', name: '负载', nameTextStyle: { color: '#9fc3e8' }, axisLabel: { color: '#9fc3e8', fontSize: 11 }, splitLine: { lineStyle: { color: 'rgba(127,166,207,0.12)' } } },
    { type: 'value', name: '进程', nameTextStyle: { color: '#ffd166' }, axisLabel: { color: '#ffd166', fontSize: 11 }, splitLine: { show: false } }
  ],
  series: [
    { name: '负载', type: 'line', data: t.load, smooth: true, showSymbol: false, lineStyle: { width: 2, color: '#21d07a' } },
    { name: '运行进程', type: 'bar', yAxisIndex: 1, data: t.procRun, barWidth: 6, itemStyle: { color: 'rgba(255,209,102,0.55)', borderRadius: [3, 3, 0, 0] } }
  ]
}))

function areaLine(name, values, color) {
  return {
    name, type: 'line', data: values, smooth: true, showSymbol: false,
    lineStyle: { width: 2, color },
    areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: color + '55' }, { offset: 1, color: color + '05' }] } }
  }
}
</script>

<style scoped>
.right-panel { width: 100%; height: 100%; display: flex; flex-direction: column; gap: 12px; }
.box { flex: 1; min-height: 0; }
</style>
