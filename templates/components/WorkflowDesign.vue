<template>
    <div style="width: 100%; height: calc(100vh - 120px);">
        <VueFlow :nodes="nodes" :edges="edges" :nodeTypes="nodeTypes">
        </VueFlow>
    </div>
</template>
<script>
const { defineAsyncComponent } = Vue;
import { VueFlow } from '/libs/vue-flow/core/vue-flow-core.mjs';

export default {
    components: {
        VueFlow,
        // ModelNode
    },
    data() {
        return {
            nodeTypes: {
                start: defineAsyncComponent(() => import(`/components/nodes/simple.vue`)),
                end: defineAsyncComponent(() => import(`/components/nodes/simple.vue`)),
                model: defineAsyncComponent(() => import(`/components/nodes/model.vue`)),
                save_image: defineAsyncComponent(() => import(`/components/nodes/save_image.vue`)),
                load_image: defineAsyncComponent(() => import(`/components/nodes/simple.vue`)),
            },
            nodes: [
                {
                    id: 'start',
                    type: 'start',
                    data: {
                        name: "开始",
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
                                threshold: 0.5
                            },
                            infer_params: {
                                threshold: 0.5
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
                                topk: 5
                            },
                            infer_params: {
                                topk: 1
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
                }
            ],
            edges: [
                {
                    id: 'start_to_load_image',
                    source: 'start',
                    target: 'load_image',
                    sourceHandle: 'outputs.input',
                    targetHandle: 'inputs.files',
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
    }
}
</script>
<style>
@import '/libs/vue-flow/core/style.css';
@import '/libs/vue-flow/core/theme-default.css';
@import '/assets/workflow.css';

.vue-flow__edge-path {
    stroke: var(--el-border-color);
    stroke-width: 2;
}
</style>