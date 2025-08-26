<script setup>
import { BaseEdge, EdgeLabelRenderer, getBezierPath, useVueFlow } from '/libs/vue-flow/core/vue-flow-core.mjs'
import { computed } from 'vue'

const props = defineProps({
  id: {
    type: String,
    required: true,
  },
  sourceX: {
    type: Number,
    required: true,
  },
  sourceY: {
    type: Number,
    required: true,
  },
  targetX: {
    type: Number,
    required: true,
  },
  targetY: {
    type: Number,
    required: true,
  },
  sourcePosition: {
    type: String,
    required: true,
  },
  targetPosition: {
    type: String,
    required: true,
  },
  markerEnd: {
    type: String,
    required: false,
  },
  style: {
    type: Object,
    required: false,
  },
})

const { removeEdges } = useVueFlow()

const path = computed(() => getBezierPath(props))
</script>

<script>
export default {
  inheritAttrs: false,
}
</script>

<template>
  <!-- You can use the `BaseEdge` component to create your own custom edge more easily -->
  <BaseEdge :id="id" :style="style" :path="path[0]" :marker-end="markerEnd" />

  <!-- Use the `EdgeLabelRenderer` to escape the SVG world of edges and render your own custom label in a `<div>` ctx -->
  <EdgeLabelRenderer>
    <div
      :style="{
        pointerEvents: 'all',
        position: 'absolute',
        transform: `translate(-50%, -50%) translate(${path[1]}px,${path[2]}px)`,
      }"
      class="nodrag nopan"
    >
      <svg class="edgebutton" width="12" height="12" @click="removeEdges(id)">
        <circle cx="5" cy="5" r="4"  />
      </svg>
    </div>
  </EdgeLabelRenderer>
</template>

<style scoped>
.edgebutton {
    cursor: pointer;
}
.edgebutton circle{
    fill: var(--el-border-color-darker);
}
.edgebutton:hover {
    transform: scale(1.1);
}

.edgebutton:hover circle {
    fill: #dc2626;
}
</style>
