<template>
    <div style="width: 100%; height: calc(100vh - 120px);">
        <VueFlow :nodes="nodes" :edges="edges">
            <template #node-model="props">
                <ModelNode :id="props.id" :data="props.data" />
            </template>
        </VueFlow>
    </div>
</template>
<script>
import {VueFlow} from '/libs/vue-flow/core/vue-flow-core.mjs';
import ModelNode from '/components/nodes/model.vue';

export default {
    components: {
        VueFlow,
        ModelNode
    },
    data() {
        return {
            nodes: [
                {
                    id: 'object_detection',
                    type: 'model',
                    data: {
                        name: "目标识别节点",
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
                        outputs: ["images", "boxes"]
                    },
                    position: { x: 250, y: 0 }
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
                    position: { x: 550, y: 0 }
                }
            ],
            edges: [
                {
                    id: 'object_detection_to_image_classification',
                    source: 'object_detection',
                    target: 'image_classification',
                    sourceHandle: 'outputs.images',
                    targetHandle: 'inputs.images',
                }
            ]
        }
    }
}
</script>
<style>
@import '/libs/vue-flow/core/style.css';
@import '/libs/vue-flow/core/theme-default.css';
@import '/assets/ports.css';
.vue-flow__edge-path {
stroke: var(--el-border-color);
stroke-width: 2;
}
</style>