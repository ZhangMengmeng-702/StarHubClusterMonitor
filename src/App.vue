<template>
  <div class="screen-wrap">
    <div class="starfield"></div>
    <div class="screen" :style="{ transform: `scale(${scale})` }">
      <DashboardHeader />

      <div class="metrics">
        <MetricCards />
      </div>

      <div class="main">
        <div class="col-left">
          <LeftPanel />
        </div>

        <div class="col-center">
          <div class="center-top">
            <ChartBox title="主机状态矩阵" sub="20 节点 · CPU/磁盘利用率热力">
              <HostMatrix />
            </ChartBox>
          </div>
          <div class="center-bottom">
            <CenterTrend />
          </div>
        </div>

        <div class="col-right">
          <RightPanel />
        </div>
      </div>

      <div class="footer">
        <AlertTicker />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import DashboardHeader from './components/DashboardHeader.vue'
import MetricCards from './components/MetricCards.vue'
import LeftPanel from './components/LeftPanel.vue'
import CenterTrend from './components/CenterTrend.vue'
import RightPanel from './components/RightPanel.vue'
import HostMatrix from './components/HostMatrix.vue'
import AlertTicker from './components/AlertTicker.vue'
import ChartBox from './components/ChartBox.vue'

const scale = ref(1)

function fit() {
  scale.value = Math.min(window.innerWidth / 1920, window.innerHeight / 1080)
}

onMounted(() => {
  fit()
  window.addEventListener('resize', fit)
})
onBeforeUnmount(() => window.removeEventListener('resize', fit))
</script>

<style scoped>
.metrics { height: 96px; margin: 6px 0; }
.main {
  flex: 1;
  min-height: 0;
  display: grid;
  grid-template-columns: 440px 1fr 440px;
  gap: 16px;
}
.col-left, .col-right { min-height: 0; }
.col-center {
  min-height: 0;
  display: grid;
  grid-template-rows: 44% 56%;
  gap: 16px;
}
.center-top, .center-bottom { min-height: 0; }
.footer { height: 56px; margin-top: 12px; }
</style>
