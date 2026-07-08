<template>
  <ChartBox title="集群性能趋势" sub="按小时聚合 · CPU/内存/磁盘/负载" class="trend-box">
    <BaseChart :option="option" />
  </ChartBox>
</template>

<script setup>
import { computed } from 'vue'
import ChartBox from './ChartBox.vue'
import BaseChart from './BaseChart.vue'
import { data } from '../utils/data.js'

const t = data.perfTrend

const option = computed(() => ({
  tooltip: { trigger: 'axis', backgroundColor: 'rgba(10,23,51,0.9)', borderColor: '#00e5ff', textStyle: { color: '#cfe6ff' } },
  legend: { top: 4, textStyle: { color: '#9fc3e8', fontSize: 12 }, itemWidth: 14, itemHeight: 8 },
  grid: { left: 10, right: 16, top: 40, bottom: 24, containLabel: true },
  xAxis: {
    type: 'category',
    data: t.times,
    boundaryGap: false,
    axisLine: { lineStyle: { color: 'rgba(127,166,207,0.4)' } },
    axisLabel: { color: '#9fc3e8', fontSize: 11, interval: Math.floor(t.times.length / 8) }
  },
  yAxis: [
    {
      type: 'value', name: '使用率 %', min: 0, max: 100,
      nameTextStyle: { color: '#9fc3e8' },
      axisLabel: { color: '#9fc3e8', fontSize: 11 },
      splitLine: { lineStyle: { color: 'rgba(127,166,207,0.12)' } }
    },
    {
      type: 'value', name: '负载', min: 0,
      nameTextStyle: { color: '#ffd166' },
      axisLabel: { color: '#ffd166', fontSize: 11 },
      splitLine: { show: false }
    }
  ],
  series: [
    lineSeries('CPU使用率', t.cpu, '#00e5ff'),
    lineSeries('内存使用率', t.mem, '#2f80ff'),
    lineSeries('磁盘利用率', t.disk, '#21d07a'),
    { ...lineSeries('系统负载', t.load, '#ffd166'), yAxisIndex: 1, areaStyle: undefined }
  ]
}))

function lineSeries(name, values, color) {
  return {
    name, type: 'line', data: values, smooth: true, showSymbol: false,
    lineStyle: { width: 2, color, shadowColor: color, shadowBlur: 8 },
    areaStyle: {
      color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: color + '55' }, { offset: 1, color: color + '05' }] }
    }
  }
}
</script>

<style scoped>
.trend-box { width: 100%; height: 100%; }
</style>
