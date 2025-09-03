<template>
    <div style="width: 100%; height: calc(100vh - 120px); position: relative;">
        <div class="tips">
            • 按Backspace键删除节点或连线<br>
            • 拖拽连线末端(靠近节点边缘处)调整连接目标<br>
            • 按住Shift键可以框选多个节点<br>
            • 按住Ctrl键可以点击选择多个节点<br>
        </div>
        <VueFlow :nodes="nodes" :edges="edges" :nodeTypes="nodeTypes" :edgesUpdatable="true" :snap-to-grid="true"
            :connect-on-click="false" @edge-update="updateConnect" @connect="newConnect" @nodesChange="applyNodeChanges"
            class="vue-flow">
        </VueFlow>
    </div>
    <!-- 添加节点按钮和菜单 -->
    <div class="node-panel-container">
        <el-popover placement="right" trigger="click">
            <template #reference>
                <el-button type="primary" circle plain size="large">
                    <el-icon size="24">
                        <svg viewBox="0 0 32 32">
                            <path fill="currentColor"
                                d="M23.52,0a8.45,8.45,0,0,0-7.8,5.22l-.09.27H4a4,4,0,0,0-4,4v3.43H16.28l.22.4.85,1.05H0V28a4,4,0,0,0,4,4H19.86a4,4,0,0,0,4-4V17.07l1.39-.14A8.56,8.56,0,0,0,23.52,0ZM3.63,23.55a1.45,1.45,0,1,1,1.43-1.44A1.44,1.44,0,0,1,3.63,23.55Zm16.57,0a1.45,1.45,0,1,1,1.44-1.44A1.44,1.44,0,0,1,20.2,23.55ZM23.58,16A7.46,7.46,0,1,1,31,8.56,7.43,7.43,0,0,1,23.58,16Z" />
                            <polygon fill="currentColor"
                                points="28.66 7.58 28.66 9.96 24.8 9.96 24.8 13.86 22.43 13.86 22.43 9.96 18.57 9.96 18.57 7.58 22.43 7.58 22.43 3.68 24.8 3.68 24.8 7.58 28.66 7.58" />
                        </svg>
                    </el-icon>
                </el-button>
            </template>
            <el-menu mode="vertical" collapse class="node-menu">
                <el-menu-item index="save" @click="console.log(toObject())">保存</el-menu-item>
                <el-menu-item-group>
                    <template #title>
                        <el-icon>
                            <Files />
                        </el-icon>
                        <span> 输入输出</span>
                    </template>
                    <el-menu-item index="start" @click="addNode('start')">请求输入</el-menu-item>
                    <el-menu-item index="end" @click="addNode('end')">请求输出</el-menu-item>
                    <el-menu-item index="load_image" @click="addNode('load_image')">加载图像</el-menu-item>
                    <el-menu-item index="save_image" @click="addNode('save_image')">保存图像</el-menu-item>
                </el-menu-item-group>

                <el-menu-item-group>
                    <template #title>
                        <el-icon>
                            <Operation />
                        </el-icon>
                        <span> 常量节点</span>
                    </template>
                    <el-menu-item index="number_const" @click="addNode('number_const')">数值常量</el-menu-item>
                    <el-menu-item index="string_const" @click="addNode('string_const')">字符串常量</el-menu-item>
                </el-menu-item-group>

                <el-menu-item-group>
                    <template #title>
                        <el-icon>
                            <HelpFilled />
                        </el-icon>
                        <span> 模型节点</span>
                    </template>
                    <el-sub-menu v-for="category in models" :index="category.category.id" class="node-menu">
                        <template #title>{{ category.category.name }}</template>
                        <template v-for="module in category.modules">
                            <el-sub-menu v-if="module.infer_params && module.infer_params.ports" :index="module.id"
                                class="node-menu" collapse-close-icon="ArrowRight" collapse-open-icon="CaretRight">
                                <template #title>{{ module.name }}</template>
                                <div class="menu-scroll-container">
                                    <el-tooltip v-for="value, key in module.models" effect="light" placement="right">
                                        <el-menu-item :index="key" @click="addNode('model', {
                                            name: module.name,
                                            params: {
                                                module_name: module.id,
                                                model_name: key,
                                                model_dir: 'weights\\' + key + '\\inference',
                                                model_params: module.infer_params?.model_params || {},
                                                infer_params: module.infer_params?.predict_params || {},
                                            },
                                            inputs: module.infer_params?.ports?.inputs || [],
                                            outputs: module.infer_params?.ports?.outputs || [],
                                        })" class="node-menu">
                                            {{ value.name }}
                                        </el-menu-item>
                                        <template #content>
                                            <span
                                                style="display: inline-block; max-width: 300px; word-wrap: break-word;">{{
                                                    value?.description }}</span>
                                        </template>
                                    </el-tooltip>
                                </div>
                            </el-sub-menu>
                        </template>

                    </el-sub-menu>
                    <el-sub-menu index="trainModels" class="trainModels">
                        <template #title>
                            <div>
                                <el-icon style="color:#409efc">
                                    <TrendCharts />
                                </el-icon>
                                <span>本地训练模型</span>
                            </div>
                        </template>
                        <div class="menu-scroll-container">
                            <el-tooltip v-for="item in trains" effect="light" placement="right">
                                <el-menu-item :index="'train_' + item.id" @click="addNode('model', item.id)"
                                    class="node-menu">
                                    {{ item.name }}
                                </el-menu-item>
                                <template #content>
                                    <span style="display: inline-block; max-width: 300px; word-wrap: break-word;">{{
                                        item?.description }}</span>
                                </template>
                            </el-tooltip>
                        </div>
                    </el-sub-menu>
                </el-menu-item-group>
            </el-menu>
        </el-popover>
    </div>
</template>
<script>
import { VueFlow, useVueFlow } from '/libs/vue-flow/core/vue-flow-core.mjs';
import nodeTypes, { createNodeData } from '/components/nodes/nodes.mjs';

export default {
    components: {
        VueFlow,
    },
    data() {
        return {
            nodeTypes,
            nodes: [],
            edges: [],
            models: [],
            trains: []
        }
    },
    /** 组件挂载时加载工作流配置 */
    async mounted() {
        try {
            // 从服务端加载工作流配置JSON文件
            const response = await fetch('/assets/workflow_config.json');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const config = await response.json();
            this.fromObject(config)
            // this.nodes = config.nodes || [];
            // this.edges = config.edges || [];
            const modelResponse = await fetch('/define/modules');
            if (!modelResponse.ok) {
                throw new Error(`HTTP error! status: ${modelResponse.status}`);
            }
            this.models = await modelResponse.json();
            const trainResponse = await fetch('/models');
            if (!trainResponse.ok) {
                throw new Error(`HTTP error! status: ${trainResponse.status}`);
            }
            this.trains = await trainResponse.json();
        } catch (error) {
            console.error('Failed to load workflow configuration:', error);
        }
    },
    setup() {
        /** 初始化vue flow相关函数 */
        const { updateEdge, addEdges,addNodes,applyNodeChanges,toObject, fromObject } = useVueFlow()
        return {
            updateEdge,
            addEdges,
            addNodes,
            applyNodeChanges,
            toObject,
            fromObject,
        }
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

        /** 添加新节点 */
        addNode(type, data = {}) {
            // 创建节点数据
            const newNode = createNodeData(type, data);
            // 添加新节点到节点列表
            this.addNodes(newNode)
        },
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
    left: 5px;
    top: 50%;
    transform: translateY(-50%);
    z-index: 100;
}

/* 节点菜单样式 */
.node-menu {
    border: none;
    width: auto;
    --el-menu-item-height: 32px;
    --el-menu-sub-item-height: 32px;
}

/* 滚动菜单容器样式 */
.menu-scroll-container {
    max-height: 400px;
    /* 设置最大高度，超出部分显示滚动条 */
    overflow-y: auto;
    /* 垂直方向滚动 */
    padding: 0px;
    min-width: 250px;
}

/* 自定义滚动条样式 */
.menu-scroll-container::-webkit-scrollbar {
    width: 8px;
    /* 滚动条宽度 */
    height: 8px;
    /* 滚动条高度 */
}

.menu-scroll-container::-webkit-scrollbar-track {
    background: transparent;
    /* 滚动条轨道背景 */
}

.menu-scroll-container::-webkit-scrollbar-thumb {
    background: #a8a8a8;
    /* 滚动条滑块颜色 */
    border-radius: 4px;
    /* 滚动条滑块圆角 */
}

.menu-scroll-container::-webkit-scrollbar-thumb:hover {
    background: #888;
    /* 滚动条滑块悬停颜色 */
}

:deep(.el-menu-item-group__title) {
    white-space: nowrap;
    width: auto;
    padding-left: 0px;
}

:deep(.trainModels .el-sub-menu__title) {
    padding-left: 0px;
}

/* 节点标题颜色 */
.node-title {
    color: #303133;
}

/* 输入输出类型端口样式 */
.input-port,
.output-port {
    cursor: pointer;
    background-color: #909399;
    border: 2px solid #909399;
}

/* 参数端口样式 */
.param-port {
    background-color: #409EFF;
    border: 2px solid #409EFF;
}

/* 确保连接线不会穿过节点 */
:deep(.vue-flow__connection-path) {
    z-index: 1;
}

/* 节点可拖拽区域样式 */
:deep(.vue-flow__handle) {
    z-index: 2;
}
</style>