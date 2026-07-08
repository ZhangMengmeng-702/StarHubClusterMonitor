<template>
  <div class="chart-box-wrap">
    <dv-border-box-8 :color="['#00e5ff', '#2f80ff']" :reverse="reverse">
      <div class="cb-inner">
        <div class="panel-title">
          {{ title }}
          <span class="sub" v-if="sub">{{ sub }}</span>
        </div>
        <div class="cb-body">
          <slot />
        </div>
      </div>
    </dv-border-box-8>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  sub: { type: String, default: '' },
  reverse: { type: Boolean, default: false }
})
</script>

<style scoped>
.chart-box-wrap {
  width: 100%;
  height: 100%;
  position: relative;
}
.cb-inner {
  width: 100%;
  height: 100%;
  padding: 10px 14px 12px;
  display: flex;
  flex-direction: column;
}
.cb-body {
  flex: 1;
  min-height: 0;
  margin-top: 6px;
}
</style>
