<template>
    <div style="width: 100%; height: calc(100vh - 120px);">
        <VueFlow :nodes="nodes" :edges="edges">
        </VueFlow>
    </div>
</template>
<script>
import { VueFlow, MarkerType } from '/libs/vue-flow/core/vue-flow-core.mjs';

export default {
    components: {
        VueFlow
    },
    data() {
        return {
            nodes: [
                {
                    id: '1',
                    type: 'input',
                    data: { label: 'Node 1' },
                    position: { x: 250, y: 0 },
                    class: 'light',
                },
                {
                    id: '2',
                    type: 'output',
                    data: { label: 'Node 2' },
                    position: { x: 100, y: 100 },
                    class: 'light',
                },
                {
                    id: '3',
                    data: { label: 'Node 3' },
                    position: { x: 400, y: 100 },
                    class: 'light',
                },
                {
                    id: '4',
                    data: { label: 'Node 4' },
                    position: { x: 150, y: 200 },
                    class: 'light',
                },
                {
                    id: '5',
                    type: 'output',
                    data: { label: 'Node 5' },
                    position: { x: 300, y: 300 },
                    class: 'light',
                },
            ],
            edges: [
                {
                    id: 'e1-2',
                    source: '1',
                    target: '2',
                    animated: true,
                },
                {
                    id: 'e1-3',
                    source: '1',
                    target: '3',
                    label: 'edge with arrowhead',
                    markerEnd: MarkerType.ArrowClosed,
                },
                {
                    id: 'e4-5',
                    type: 'step',
                    source: '4',
                    target: '5',
                    label: 'Node 2',
                    style: { stroke: 'orange' },
                    labelBgStyle: { fill: 'orange' },
                },
                {
                    id: 'e3-4',
                    type: 'smoothstep',
                    source: '3',
                    target: '4',
                    label: 'smoothstep-edge',
                },
            ]
        }
    }
}
</script>
<style>
/* import the necessary styles for Vue Flow to work */
@import '/libs/vue-flow/core/style.css';
/* import the default theme, this is optional but generally recommended */
@import '/libs/vue-flow/core/theme-default.css';
</style>