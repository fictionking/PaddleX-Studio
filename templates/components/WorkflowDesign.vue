<template>
    <div style="width: 100%; height: calc(100vh - 120px); position: relative;">
        <div class="tips">
            • 按Backspace键删除节点或连线<br>
            • 拖拽连线末端(靠近节点边缘处)调整连接目标<br>
            • 按住Shift键可以框选多个节点<br>
            • 按住Ctrl键可以点击选择多个节点<br>
        </div>
        <VueFlow :nodes="nodes" :edges="edges" :nodeTypes="nodeTypes" :edgesUpdatable="true" :snap-to-grid="true"
            :connect-on-click="false" @edge-update="updateConnect" class="vue-flow">
        </VueFlow>
    </div>
</template>
<script>
const { defineAsyncComponent, markRaw } = Vue;
import { VueFlow, useVueFlow } from '/libs/vue-flow/core/vue-flow-core.mjs';

export default {
    components: {
        VueFlow,
    },
    data() {
        return {
            nodeTypes: {
                start: markRaw(defineAsyncComponent(() => import(`/components/nodes/simple.vue`))),
                end: markRaw(defineAsyncComponent(() => import(`/components/nodes/simple.vue`))),
                model: markRaw(defineAsyncComponent(() => import(`/components/nodes/model.vue`))),
                save_image: markRaw(defineAsyncComponent(() => import(`/components/nodes/save_image.vue`))),
                load_image: markRaw(defineAsyncComponent(() => import(`/components/nodes/simple.vue`))),
                number_const: markRaw(defineAsyncComponent(() => import(`/components/nodes/const.vue`))),
                string_const: markRaw(defineAsyncComponent(() => import(`/components/nodes/const.vue`))),
            },
            nodes: [
                {
                    id: 'start',
                    type: 'start',
                    data: {
                        name: "开始",
                        fixName: true,
                        params: {
                        },
                        inputs: [],
                        outputs: ["input"]
                    },
                    position: { x: 0, y: 0 }
                },
                {
                    id: 'end',
                    type: 'end',
                    data: {
                        name: "结束",
                        fixName: true,
                        params: {
                        },
                        inputs: ["output"],
                        outputs: []
                    },
                    position: { x: 1000, y: 0 }
                },
                {
                    id: 'load_image',
                    type: 'load_image',
                    data: {
                        name: "加载图像",
                        params: {
                        },
                        inputs: ["files"],
                        outputs: ["images", "count"]
                    },
                    position: { x: 200, y: 0 }
                },
                {
                    id: 'object_detection',
                    type: 'model',
                    data: {
                        name: "目标识别",
                        params: {
                            module_name: "object_detection",
                            model_name: "PP-YOLOE_plus-L",
                            model_dir: "weights\PP-YOLOE_plus-L\inference",
                            model_params: {
                                threshold: {
                                    type: "number",
                                    value: 0.5,
                                    min: 0,
                                    max: 1,
                                    step: 0.1
                                }
                            },
                            infer_params: {
                                threshold: {
                                    type: "number",
                                    value: 0.5,
                                    min: 0,
                                    max: 1,
                                    step: 0.1
                                },
                                prompt: {
                                    type: "text",
                                    value: `识别所有物体`,
                                },
                                use_prompt: {
                                    type: "bool",
                                    value: false,
                                    trueLabel: "使用",
                                    falseLabel: "不使用",
                                }
                            }
                        },
                        inputs: ["images"],
                        outputs: ["images", "boxes", "count"]
                    },
                    position: { x: 400, y: 0 }
                },
                {
                    id: "image_classification",
                    type: "model",
                    data: {
                        name: "图像分类节点",
                        params: {
                            module_name: "image_classification",
                            model_name: "PP-HGNetV2-B6",
                            model_dir: "weights\PP-HGNetV2-B6\inference",
                            model_params: {
                                topk: {
                                    type: "number",
                                    value: 5,
                                    min: 1,
                                    max: 10,
                                    step: 1
                                }
                            },
                            infer_params: {
                                topk: {
                                    type: "number",
                                    value: 1,
                                    min: 1,
                                    max: 10,
                                    step: 1
                                }
                            }
                        },
                        inputs: ["images"],
                        outputs: ["labels"]
                    },
                    position: { x: 700, y: 0 }
                },
                {
                    id: "image_output",
                    type: "save_image",
                    data: {
                        name: "保存图像",
                        params: {
                            format: 'png',
                            path: 'output/images',
                            filename: 'image'
                        },
                        inputs: ["images"],
                        outputs: ["files"]
                    },
                    position: { x: 700, y: 300 }
                },
                {
                    id: "topk_const",
                    type: "number_const",
                    data: {
                        name: "TopK",
                        params: {
                            value: 0
                        },
                        inputs: [],
                        outputs: ["value"]
                    },
                    position: { x: 400, y: 400 }
                }
            ],
            edges: [
                {
                    id: 'start_to_load_image',
                    source: 'start',
                    target: 'load_image',
                    sourceHandle: 'outputs.input',
                    targetHandle: 'inputs.files',
                    style: ".vue-flow"
                },
                {
                    id: 'load_image_to_object_detection',
                    source: 'load_image',
                    target: 'object_detection',
                    sourceHandle: 'outputs.images',
                    targetHandle: 'inputs.images',
                },
                {
                    id: 'object_detection_to_image_classification',
                    source: 'object_detection',
                    target: 'image_classification',
                    sourceHandle: 'outputs.images',
                    targetHandle: 'inputs.images',
                },
                {
                    id: 'topk_const_to_image_classification',
                    source: 'topk_const',
                    target: 'image_classification',
                    sourceHandle: 'outputs.value',
                    targetHandle: 'params.infer_params.topk',
                },
                {
                    id: 'object_detection_to_image_output',
                    source: 'object_detection',
                    target: 'image_output',
                    sourceHandle: 'outputs.images',
                    targetHandle: 'inputs.images',
                },
                {
                    id: 'image_classification_to_end',
                    source: 'image_classification',
                    target: 'end',
                    sourceHandle: 'outputs.labels',
                    targetHandle: 'inputs.output',
                }
            ]
        }
    },
    setup() {
        /** 初始化vue flow相关函数 */
        const { onInit, onNodeDragStop, onConnect, updateEdge, addEdges, setViewport, toObject } = useVueFlow()
        return {
            onInit,
            onNodeDragStop,
            onConnect,
            updateEdge,
            addEdges,
            setViewport,
            toObject
        }
    },
    async created() {
        this.onConnect(this.newConnect)
    },
    methods: {
        newConnect(connection) {
            if (this.checkConnect(connection)) {
                this.addEdges(connection)
            }
        },
        updateConnect({ edge, connection }) {
            if (this.checkConnect(connection)) {
                this.updateEdge(edge, connection)
            }
        },
        checkConnect(connection) {
            if (connection.sourceHandle.startsWith('outputs.')
                && (connection.targetHandle.startsWith('inputs.') ||
                    connection.targetHandle.startsWith('params.'))) {
                return true
            }
            return false
        }
    }
}
</script>
<style scoped>
@import '/libs/vue-flow/core/style.css';
@import '/libs/vue-flow/core/theme-default.css';
@import '/assets/workflow.css';

.tips {
    position: absolute;
    top: 0px;
    right: 0px;
    padding: 5px 10px;
    border-radius: 4px;
    font-size: 12px;
    color: var(--el-text-color-disabled);
}

:deep(.vue-flow .vue-flow__edge.selected .vue-flow__edge-path) {
    stroke: rgb(224, 154, 2) !important;
}

:deep(.vue-flow .vue-flow__edge.updating .vue-flow__edge-path) {
    stroke: var(--el-text-color-regular) !important;
}

:deep(.vue-flow .vue-flow__edge-path) {
    stroke: var(--el-border-color) !important;
    stroke-width: 3 !important;
}
</style>