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
    <!-- 添加节点按钮和面板 -->
    <div class="node-panel-container">
        <el-button type="primary" icon="Plus" circle size="large" @click="toggleNodePanel" :class="{ 'active': showNodePanel }">
        </el-button>

        <div class="node-panel" :class="{ 'show': showNodePanel }">
            <div class="panel-header">
                <h3>节点类型</h3>
            </div>
            <div class="panel-content">
                <div class="node-type-group">
                    <h4>基础节点</h4>
                    <button class="node-type-button" @click="addNode('start')">开始节点</button>
                    <button class="node-type-button" @click="addNode('end')">结束节点</button>
                    <button class="node-type-button" @click="addNode('load_image')">加载图像</button>
                    <button class="node-type-button" @click="addNode('save_image')">保存图像</button>
                </div>

                <div class="node-type-group">
                    <h4>常量节点</h4>
                    <button class="node-type-button" @click="addNode('number_const')">数值常量</button>
                    <button class="node-type-button" @click="addNode('string_const')">字符串常量</button>
                </div>

                <div class="node-type-group">
                    <h4>模型节点</h4>
                    <button class="node-type-button" @click="addNode('model', 'object_detection')">目标识别</button>
                    <button class="node-type-button" @click="addNode('model', 'image_classification')">图像分类</button>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
const { defineAsyncComponent, markRaw, ref } = Vue;
import { VueFlow, useVueFlow } from '/libs/vue-flow/core/vue-flow-core.mjs';

export default {
    components: {
        VueFlow,
    },
    data() {
        return {
            showNodePanel: false,
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
        },
        /** 切换节点面板显示状态 */
        toggleNodePanel() {
            this.showNodePanel = !this.showNodePanel;
        },
        /** 添加新节点 */
        addNode(type, subtype = '') {
            // 生成唯一ID
            const id = `${type}_${Date.now()}`;

            // 根据节点类型创建不同的节点数据
            let newNode = {
                id: id,
                type: type,
                position: { x: 300, y: 200 },
                data: {
                    name: '',
                    params: {},
                    inputs: [],
                    outputs: []
                }
            };

            // 根据节点类型设置特定属性
            switch (type) {
                case 'start':
                    newNode.data.name = '开始';
                    newNode.data.fixName = true;
                    newNode.data.outputs = ['input'];
                    break;
                case 'end':
                    newNode.data.name = '结束';
                    newNode.data.fixName = true;
                    newNode.data.inputs = ['output'];
                    break;
                case 'load_image':
                    newNode.data.name = '加载图像';
                    newNode.data.inputs = ['files'];
                    newNode.data.outputs = ['images', 'count'];
                    break;
                case 'save_image':
                    newNode.data.name = '保存图像';
                    newNode.data.inputs = ['images'];
                    newNode.data.outputs = ['files'];
                    newNode.data.params = {
                        format: 'png',
                        path: 'output/images',
                        filename: 'image'
                    };
                    break;
                case 'number_const':
                    newNode.data.name = '数值常量';
                    newNode.data.outputs = ['value'];
                    newNode.data.params = {
                        value: 0
                    };
                    break;
                case 'string_const':
                    newNode.data.name = '字符串常量';
                    newNode.data.outputs = ['value'];
                    newNode.data.params = {
                        value: ''
                    };
                    break;
                case 'model':
                    if (subtype === 'object_detection') {
                        newNode.data.name = '目标识别';
                        newNode.data.params = {
                            module_name: 'object_detection',
                            model_name: 'PP-YOLOE_plus-L',
                            model_dir: 'weights\PP-YOLOE_plus-L\inference',
                            model_params: {
                                threshold: {
                                    type: 'number',
                                    value: 0.5,
                                    min: 0,
                                    max: 1,
                                    step: 0.1
                                }
                            },
                            infer_params: {
                                threshold: {
                                    type: 'number',
                                    value: 0.5,
                                    min: 0,
                                    max: 1,
                                    step: 0.1
                                },
                                prompt: {
                                    type: 'text',
                                    value: '识别所有物体'
                                },
                                use_prompt: {
                                    type: 'bool',
                                    value: false,
                                    trueLabel: '使用',
                                    falseLabel: '不使用'
                                }
                            }
                        };
                        newNode.data.inputs = ['images'];
                        newNode.data.outputs = ['images', 'boxes', 'count'];
                    } else if (subtype === 'image_classification') {
                        newNode.data.name = '图像分类';
                        newNode.data.params = {
                            module_name: 'image_classification',
                            model_name: 'PP-HGNetV2-B6',
                            model_dir: 'weights\PP-HGNetV2-B6\inference',
                            model_params: {
                                topk: {
                                    type: 'number',
                                    value: 5,
                                    min: 1,
                                    max: 10,
                                    step: 1
                                }
                            },
                            infer_params: {
                                topk: {
                                    type: 'number',
                                    value: 1,
                                    min: 1,
                                    max: 10,
                                    step: 1
                                }
                            }
                        };
                        newNode.data.inputs = ['images'];
                        newNode.data.outputs = ['labels'];
                    }
                    break;
            }

            // 添加新节点到节点列表
            this.nodes.push(newNode);

            // 关闭节点面板
            this.showNodePanel = false;
        }
    }
}
</script>
<style scoped>
/* @import '/libs/vue-flow/core/style.css'; */
/* @import '/libs/vue-flow/core/theme-default.css'; */
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

:deep(.vue-flow__handle) {
    border: 2px solid rgba(0, 0, 0, 0.7) !important;
}

/* 节点面板容器样式 */
.node-panel-container {
    position: absolute;
    left: 0px;
    top: 50%;
    transform: translateY(-50%);
    z-index: 100;
}

/* 添加节点按钮样式 */
.add-node-button {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 120px;
    background-color: var(--el-color-primary);
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    transition: all 0.3s;
    writing-mode: vertical-rl;
    text-orientation: mixed;
    padding: 10px 0;
}

.add-node-button:hover {
    background-color: var(--el-color-primary-light-3);
}

.add-node-button.active {
    background-color: var(--el-color-primary-dark-2);
}

.add-node-button span:first-child {
    font-size: 24px;
    font-weight: bold;
    margin-bottom: 8px;
}

/* 节点面板样式 */
.node-panel {
    position: absolute;
    left: 60px;
    top: 0;
    width: 200px;
    max-height: 500px;
    background-color: white;
    border-radius: 4px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    overflow: hidden;
    transform: translateX(-20px);
    opacity: 0;
    visibility: hidden;
    transition: all 0.3s;
}

.node-panel.show {
    transform: translateX(0);
    opacity: 1;
    visibility: visible;
}

/* 面板头部样式 */
.panel-header {
    padding: 10px 15px;
    background-color: var(--el-color-primary-light-9);
    border-bottom: 1px solid var(--el-border-color-light);
}

.panel-header h3 {
    margin: 0;
    font-size: 16px;
    color: var(--el-text-color-primary);
}

/* 面板内容样式 */
.panel-content {
    padding: 10px;
    max-height: 420px;
    overflow-y: auto;
}

/* 节点类型分组样式 */
.node-type-group {
    margin-bottom: 15px;
}

.node-type-group:last-child {
    margin-bottom: 0;
}

.node-type-group h4 {
    margin: 0 0 8px 0;
    font-size: 14px;
    color: var(--el-text-color-regular);
    padding-left: 5px;
    border-left: 3px solid var(--el-color-primary);
}

/* 节点类型按钮样式 */
.node-type-button {
    display: block;
    width: 100%;
    padding: 8px 12px;
    margin-bottom: 5px;
    background-color: var(--el-fill-color-blank);
    border: 1px solid var(--el-border-color-lighter);
    border-radius: 4px;
    text-align: left;
    cursor: pointer;
    transition: all 0.2s;
    font-size: 14px;
    color: var(--el-text-color-primary);
}

.node-type-button:hover {
    background-color: var(--el-color-primary-light-9);
    border-color: var(--el-color-primary);
    color: var(--el-color-primary);
}

.node-type-button:last-child {
    margin-bottom: 0;
}
</style>